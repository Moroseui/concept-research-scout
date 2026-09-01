# Interpretation — idea 045, probe contract v3 (pooled-slope attenuation attribution)

Results bundle: `probes/045/results/results_v4/`, imported at commit
`14b183f0b5696bf7ce1d5320d2b71e95353447a4` (import receipt
`probes/045/results/results_v4.import.json`: `manifest_sha256`
`3bbdd2fd47917fd3305002276d346c045e7a75bb7e7a097d2b9afe74573c3b68`,
`file_count` 13, `source_commit` null — locally executed bundle under the
local-import ancestry lane). All citations below are relative to that
bundle root at that commit unless an explicit repository path is given.

Governing identity: contract blob
`b1e283613d4fd47c77bfd1f2838a54791eb25954` [cite: resolved_config.json |
contract_blob | value], `contract_version` 3 [cite: resolved_config.json |
contract_version | value], matching the human approval marker of
2026-09-01T06:57:20Z (`ideas/045/HUMAN_APPROVED_PROBE`, which also pins
registry sha `1c0e82a6…`) and the current `ideas/045/probe_contract.yaml`
byte-for-byte (git hash-object recomputed during this interpretation).
Inputs are the two frozen tables of the imported idea-023 take-13 bundle,
identity-pinned to the contract's `frozen_inputs` and re-verified in-run:
`bin_tissue_audit.csv` sha256 `35e896df…` and `per_patient.csv` sha256
`1d01551c…` [cite: input_manifest.csv | path=…bin_tissue_audit.csv,
…per_patient.csv | sha256].

**Where the uncertainty lives.** This is the lineage's first
outcome-reading probe. The scientific point estimates are deterministic
functions of the two pinned inputs; the only randomness is the
contract-predeclared 10,000-replicate patient-cluster bootstrap at frozen
seed 20260901 [cite: bootstrap_summary.json | seed,
replicates_requested | values], which is the contract's case-level
uncertainty machinery. The single-seed training rule does not apply (no
training occurs); effect claims below are judged exactly against these
clustered percentile intervals and carry exactly the strength the
contract's frozen `interpretation_rule` assigns them — no more.

Bottom line, in the contract's own permitted vocabulary: **adjustment for
measured median-HU imbalance did not explain the parent reversal at
achieved precision.** Status `DECISIVE_MEASURED_EXPLANATION_FAILURE`
[cite: summary.json | status | value]: after adjusting the band means to
pooled zero centered HU imbalance, band 2 remains negative
(−0.03133128471039588, 95% CI [−0.05589866048677166,
−0.00789029340507566]) and band 3 remains positive
(0.022404903919524183, 95% CI [0.0038892800799788215,
0.043408163548312576]) — both patient-bootstrap intervals exclude zero on
the parent's original sides [cite: summary.json | primary_metric |
adjusted_band2_mean, adjusted_band2_ci95, adjusted_band3_mean,
adjusted_band3_ci95, opposite_sign_precise]. Idea-023's opposite-signed
band-2/band-3 pattern survives the measured tissue-composition
adjustment intact.

---

## Demonstrates

Deterministic computations on frozen, hash-pinned inputs, plus the
pre-registered clustered-bootstrap machinery; each claim cites its exact
source.

1. **The probe executed validly end to end under its contract.** One
   variant of a maximum of one ran (`Variant 1/1 — approved v3
   attribution; seed=20260901`) [cite: run_log.txt | phase 1 | line 2];
   the start and end determinism manifests — which re-hash both input
   files — agree exactly [cite: run_log.txt | phase 4 | final line]; no
   network calls [cite: resolved_config.json | network_calls | value];
   smoke off [cite: summary.json | smoke | value]; the pre-approval
   harness self-check passed at 2026-09-01T07:10:41Z
   [cite: probes/045/verification.json | passed, checked_at | values];
   run.py sha256 `69622688…` matches the round-1 cross-family APPROVE
   (`ideas/045/probe_review.md`), recomputed during this interpretation.

2. **Outcome-access ordering held.** The 198-row split was frozen and
   hashed before the outcome file was first opened
   [cite: split_manifest.json | created_before_outcome_file_open |
   value], split hash `6446ad66…` [cite: split_manifest.json | sha256 |
   value] — byte-identical to the split hash of both executed
   feasibility audits [cite: probes/045/results/results_v3/
   split_manifest.json | sha256 | value], so the outcome analysis ran on
   exactly the frozen 198 case-band rows certified feasible by v2. Zero
   reserved cases were accessed [cite: summary.json |
   reserved_cases_accessed | value]; the 49 reserved cases remain
   untouched.

3. **Cohort, join, and exclusion accounting are complete.** 99 unique
   cases, 198 analysis rows [cite: summary.json | unique_cases,
   analysis_rows | values]; audit 594 total rows → 396 selected, outcome
   297 → 198 [cite: input_manifest.csv | both rows | total_rows,
   selected_rows]; 297 rows excluded in 297 per-row records, every one
   with reason `non_primary_band` [cite: summary.json |
   excluded_input_rows, exclusion_records | values; cite: exclusions.csv
   | all rows | reason].

4. **The parent reconstruction is transcription-exact, not merely
   directional.** The equal-patient-weight unadjusted band means computed
   here — band 2 −0.03200187198047477, band 3 0.02307549118960302
   [cite: summary.json | unadjusted_band2_mean, unadjusted_band3_mean |
   values] — equal the parent census values digit-for-digit
   [cite: probes/023/results/results_v2/per_stratum_summary.csv |
   stratum=2, stratum=3 | mean_d]. The in-run parent-reconstruction gate
   (band 2 negative, band 3 positive) passed before any bootstrap cost
   was spent.

5. **The pre-registered decisive rule fired on its exact frozen terms.**
   The contract's `interpretation_rule` grants
   `DECISIVE_MEASURED_EXPLANATION_FAILURE` if and only if the adjusted
   band-2 interval lies entirely below zero and the adjusted band-3
   interval entirely above zero. Both conditions hold (intervals quoted
   in the bottom line; `opposite_sign_precise: true`
   [cite: summary.json | primary_metric | opposite_sign_precise]). The
   bootstrap completed 10,000 of 10,000 replicates with zero failures
   [cite: bootstrap_summary.json | replicates_completed,
   failed_replicates | values], so the abort-on-any-failure clause was
   never engaged.

6. **The single authorized model is the one that was fit.** Three
   coefficients — intercept −0.03133128471039588, band-3 indicator
   0.053736188629920065, beta_HU 0.0010664775781553057 — at design rank
   3, maximum row leverage 0.15486441040641785, pooled centering
   constant −0.15909079349402225 [cite: model_diagnostics.json |
   coefficients, design_rank, maximum_leverage,
   pooled_hu_imbalance_center | values]. No interaction, transform, or
   second model exists in the bundle; the per-patient audit table carries
   the complete fitted values, residuals, and leverages of that one fit
   [cite: per_patient_attribution.csv | all 198 rows | fitted_d,
   residual_d, leverage].

## Suggests

Interpretive steps beyond the frozen rule; every number cited, the
reading mine.

1. **The measured explanation fails structurally, not marginally.**
   Adjustment moved each band mean by only ±0.0006705872700788901
   (band-2 change 95% CI [−0.0011545729065425532,
   +0.0029349507985416243]; band-3 change the exact mirror)
   [cite: bootstrap_summary.json | point_estimates, intervals |
   band2_adjustment_change, band3_adjustment_change], and the absolute
   band gap changed by −0.0013411745401577246 (95% CI
   [−0.005869901597083304, +0.002309145813085035])
   [cite: bootstrap_summary.json | point_estimates, intervals |
   absolute_band_difference_change] against an adjusted gap of
   0.053736188629920065 (95% CI [0.025413321882444898,
   0.08507011789496013]) [cite: bootstrap_summary.json |
   point_estimates, intervals | adjusted_band3_minus_band2]. Even at the
   bootstrap extremes, common-slope HU adjustment dents the band gap by
   less than 0.006 of its ~0.054 size. The mirror-exact band changes are
   algebra, not coincidence: with 99 rows per band and pooled-mean
   centering, the two band-mean centered imbalances are equal and
   opposite, so bands 2 and 3 carry nearly the same average HU
   imbalance — a common slope of any magnitude could barely have moved
   this band contrast. The decisive verdict is therefore robust to the
   slope's imprecision, not dependent on it.

2. **The pooled slope itself is small and imprecise.** beta_HU is
   0.0010664775781553057 d-units per HU of Q1-minus-Q4 imbalance, 95% CI
   [−0.001291573690909813, +0.003726706840533707]
   [cite: summary.json | beta_hu, beta_hu_ci95 | values] — an interval
   spanning zero. Under the contract this licenses no claim in either
   direction about association (see Does not establish); its role here
   is only that the ASSOCIATION arm's precondition also failed, so the
   classification did not turn on rule precedence.

3. **Row-level heterogeneity runs against a simple attenuation story,
   echoing the critique's pre-registration reading.** The largest
   positive imbalance row (sub-stroke0183, band 2, +18.0 HU) has
   observed d +0.24045261669024046 against fitted −0.011965021539448069
   — residual +0.25241763822968855 [cite: per_patient_attribution.csv |
   case_id=sub-stroke0183, stratum=2 | hu_imbalance, d, fitted_d,
   residual_d]; the most negative imbalance row (sub-stroke0109, band 3,
   −28.0 HU) has observed d exactly 0.0
   [cite: per_patient_attribution.csv | case_id=sub-stroke0109,
   stratum=3 | hu_imbalance, d]. Extreme attenuation imbalance and
   extreme outcome contrast do not coincide in these data.

4. **The persisting reversal remains a property of means, not of the
   typical patient.** The parent's per-band median d is ≈0 in both
   primary bands (band 2 −0.0005886681383370125, band 3
   0.000556250836852953) [cite: probes/023/results/results_v2/
   per_stratum_summary.csv | stratum=2, stratum=3 | median_d]. What
   survived adjustment is the equal-patient-weight mean contrast the
   card deliberately scoped its claims to; a minority of patients still
   drives it.

## Does not establish

- **Any association claim, positive or null, between HU imbalance and
  d.** The contract prohibits reading a null or imprecise slope as
  evidence of no association or independence; beta_HU's interval spans
  zero and licenses nothing.
- **That tissue composition plays no role in the parent reversal.** The
  decisive failure is scoped to the *measured* explanation: a linear,
  common-slope effect of Q1-minus-Q4 *median* NCCT attenuation
  imbalance. By construction the approved model cannot represent
  opposite-signed HU effects in bands 2 and 3 (the v3 contract's open
  question, answered "yes for this one exploratory analysis" at
  approval); a band-antisymmetric attenuation effect would cancel in the
  pooled slope and was not examinable here. The v1 interaction design
  that could have examined it was refused as numerically infeasible
  (condition number 38.89 against the ≤30 bound
  [cite: probes/045/results/results_v2/design_diagnostics.json |
  condition_number | value]). Nonlinear, non-median (e.g. IQR- or
  tail-based), or spatially structured composition effects are likewise
  unexamined.
- **Any causal reading.** Severity as a common cause of attenuation
  imbalance and d was never adjusted for; the card names it an open
  alternative throughout.
- **Median NCCT attenuation as a validated tissue-type or viability
  measurement** (Alzahrani 2023 bounds this, per the keystone screen).
- **Any model-use claim.** No model was probed; this is a Rung-0
  attribution study on frozen tables.
- **Generalization** beyond these 99 analyzed cases, the released
  icobrain-cva pipeline, and this measured proxy.
- **What actually causes idea-023's reversal.** One named explanation is
  closed at achieved precision under this specification; the reversal
  itself remains unexplained.

## Validity failures

None. Walking the contract's `invalidating_failures`: authority — the
marker binds the live contract blob recorded in the bundle
[cite: resolved_config.json | contract_blob | value]; input identity —
both sha256 pins re-verified in-run and recorded [cite:
input_manifest.csv | both rows | sha256]; join/cohort — 99 cases per
band, no duplicates, no reserved case (the reserved-path guard and
absence from the pinned inputs); parent reconstruction —
transcription-exact (Demonstrates 4); analysis deviation — one model,
rank 3, no interaction column exists; bootstrap — 10,000/10,000 with
zero failed replicates [cite: bootstrap_summary.json |
replicates_completed, failed_replicates | values]; leakage/scope — zero
reserved cases accessed, split frozen before outcome open; lineage — the
v1/v2 bundles (`results_v2/`, `results_v3/`) are untouched and this run
wrote a fresh `results_v4` from a clean output root
[cite: resolved_config.json | output_dir | value]; outputs — all nine
contract-required artifacts present plus split and determinism
manifests (13 files) [cite: probes/045/results/results_v4.import.json |
file_count | value]. This is a **valid pre-registered negative**, not a
stopped or degraded run.

## Findings, stated positively and negatively

- **Negative finding (the result):** the contract's pre-registered
  `negative_pattern` fired on its exact frozen terms. Adjusting
  idea-023's band-2 and band-3 equal-patient-weight mean final-infarct
  contrasts for Q1-minus-Q4 median NCCT attenuation imbalance leaves
  both contrasts opposite-signed with patient-bootstrap intervals
  excluding zero. Per the contract's claim discipline, this decisively
  shows **only** that adjustment for this median-HU imbalance did not
  explain the parent reversal at achieved precision. The card's central
  question — did tissue composition, as measured by this proxy, create
  the sign reversal? — is answered **no** at achieved precision.
- **Positive findings:** none scientific. Operationally: the parent
  band means were reconstructed digit-for-digit from the frozen inputs
  (Demonstrates 4), and the v2 feasibility certification was borne out —
  the design fit without numerical incident on the first and only
  outcome read of this lineage.

## Authorized variants

One variant was authorized (`maximum_variants: 1`) and exactly one ran:
the approved pooled-slope attribution fit with its seed-20260901
10,000-replicate patient-cluster bootstrap, smoke off
[cite: run_log.txt | phase 1 | line 2; cite: summary.json |
variants_run, smoke | values]. One seed of a maximum of one. No other
model, threshold, transform, band, or bootstrap rule was executed. The
executed v1 and v2 feasibility audits are separate completed historical
contracts cited above as lineage evidence only; the harness self-check
receipt (`probes/045/verification.json`) is a code-review artifact, not
a scientific variant.

## Next decision

**PAUSE.** The revision of 2026-09-01 promoted this attribution analysis
to the whole candidate, and its pre-registered decisive arm has now
executed: the measured tissue-composition explanation did not account
for the parent reversal. Under the card's own terms nothing further is
authorized — the contract's stopping rule is spent, the card prohibits
authorizing the removed tissue-gated census, and the lineage rule that
"taste is not grounds for a third operationalization" applies to any
temptation to re-operationalize tissue composition on these same opened
outcomes. Concretely:

1. After cross-family review of this interpretation, ratify with status
   PAUSED. The reason (a field, not a status): pre-registered decisive
   negative for the measured explanation; question answered at achieved
   precision; no further analysis authorized under this card.
2. Successor paths, each requiring a new candidate through the normal
   pipeline with its own novelty audit: (a) a band-specific attenuation
   specification that first solves the v1 conditioning failure (the only
   design that could see opposite-signed HU effects); (b) a different
   composition measurement (non-median attenuation statistics, or an
   external tissue-probability map); (c) a severity-adjustment design
   addressing the common-cause alternative. None inherits this card's
   queue position.
3. Ops note for the record-result/ratification lane: the executed
   attribution probe is not yet a node in `ideas/045/registry.yaml`
   (which the approval marker pins at sha `1c0e82a6…` with the two
   feasibility nodes); adding the v3 node with its three
   contract-declared terminal statuses and re-ratifying is the queued
   governance act probe_review finding 7 anticipated.

The 49 reserved cases remain unread. What idea 045 leaves behind is a
clean, citable close of its own question: the reversal idea-023 found is
not an artifact of the tissue-composition difference its audit measured.
