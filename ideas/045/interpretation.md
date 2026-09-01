# Interpretation — idea 045, probe contract v2 (outcome-blind pooled-slope design feasibility)

Results bundle: `probes/045/results/results_v3/`, imported at commit
`7de47840d02d601dc802e151ecc9abde68d8f0ed` (import receipt
`probes/045/results/results_v3.import.json`: `manifest_sha256`
`1e104c8b620b946ffe2d58be328067c2a9b786d0096a74736ed6676958baeed1`,
`file_count` 12).
All citations below are relative to that bundle root at that commit unless
an explicit repository path is given.

Governing identity: contract blob `5615afea1e2f8309745a2d6558bd9118e5e9f1f3`
[cite: resolved_config.json | contract_blob | value], `contract_version` 2
[cite: resolved_config.json | contract_version | value], matching the human
approval marker of 2026-09-01T05:36:24Z (`ideas/045/HUMAN_APPROVED_PROBE`)
and the current `ideas/045/probe_contract.yaml` byte-for-byte (git
hash-object recomputed during this interpretation). Inputs are the two
frozen tables of the imported idea-023 take-13 bundle, identity-pinned to
the contract's `frozen_inputs`: `bin_tissue_audit.csv` sha256 `35e896df…`
and `per_patient.csv` sha256 `1d01551c…` [cite: input_manifest.csv |
path=…bin_tissue_audit.csv, …per_patient.csv | sha256].

The probe is fully deterministic (no training, no sampling, no bootstrap;
`randomness: "None"` in the contract; seed recorded as 0 and unused for any
draw [cite: resolved_config.json | seed | value]). The seed-count rule for
stochastic procedures therefore does not apply; case-level sensitivity is
covered inside the probe by the contract's own leave-one-patient-out
diagnostic, which this run extends to per-deletion leverage. Effect-size
language about the scientific question does not arise: zero outcome values
were read [cite: summary.json | outcome_values_read | value].

Bottom line, in the contract's own permitted vocabulary: **the frozen
bands-2/3 pooled-slope attenuation-imbalance design IS sufficiently
conditioned and distributed across patients for a separately governed
attribution analysis.** Status `POSITIVE_PATTERN`,
`contractual_gate_satisfied: true` [cite: summary.json | status,
contractual_gate_satisfied | value]. Per the contract's interpretation
clause, this "establishes computational feasibility only"; it does not
validate slope homogeneity, establish any association, or authorize
reading `d`.

---

## Demonstrates

Deterministic computations on frozen, hash-pinned inputs; each is exact,
not an estimate.

1. **The probe executed validly end to end under its contract.** One
   variant of a maximum of one ran (`Variant 1/1`, seed 0)
   [cite: run_log.txt | phase 1 | line 2]; the start and end determinism
   manifests agree exactly [cite: run_log.txt | phase 4 | final line]; no
   network calls were authorized or configured [cite: resolved_config.json
   | network_calls | value]; smoke mode was off [cite: summary.json |
   smoke | value].

2. **Outcome blindness held.** Zero observed `d` values were parsed or
   retained [cite: summary.json | outcome_values_read | value]; the
   198-row split was frozen before the outcome file was first opened
   [cite: split_manifest.json | created_before_outcome_file_open | value],
   with split hash `6446ad66…` [cite: split_manifest.json | sha256 |
   value]; zero reserved cases were accessed [cite: summary.json |
   reserved_cases_accessed | value]. The split hash is byte-identical to
   the executed v1 audit's split
   [cite: probes/045/results/results_v2/split_manifest.json | sha256 |
   value], demonstrating that v2 analyzed exactly the same frozen 198
   case-band rows — the specification changed, the cohort did not.

3. **All join and integrity gates passed.** Exactly 99 unique cases
   [cite: summary.json | unique_cases | value], 99 per primary band
   [cite: design_diagnostics.json | band_support.2, band_support.3 | n],
   one Q1 and one Q4 audit row and one key row per case-band, all derived
   values finite (no value-failure exit occurred; the run reached phase 4).
   Row accounting is complete and reconstructible: audit 594 total rows →
   396 selected; keys 297 → 198 selected [cite: input_manifest.csv | both
   rows | total_rows, selected_rows]; 297 rows excluded in 2 records, all
   with reason `non_primary_band` (198 audit band-1 rows, 99 per-patient
   band-1 rows) [cite: exclusions.csv | case_id=* | count]; 198 analysis
   rows [cite: summary.json | analysis_rows | value].

4. **The frozen pooled-slope design passes the complete feasibility
   conjunction — all ten recorded gates are true** [cite:
   design_diagnostics.json | gates | all keys]:
   - **Conditioning passes.** Primary condition number
     **20.222895326167112** against the frozen ≤ 30 bound
     [cite: design_diagnostics.json | condition_number | value]; the
     matrix has rank 3 [cite: design_diagnostics.json | rank | value] with
     singular values 14.089047615314039, 1.0066594185504498,
     0.6966879563028607 [cite: design_diagnostics.json | singular_values |
     list].
   - **Exposure support passes under the v2 pooled rule.** The pooled
     exposure lands on 29 distinct values (≥ 20 required) across 198 rows,
     IQR 4.0, range −28.0 to +18.0 [cite: design_diagnostics.json |
     pooled_support | distinct_values, n, iqr, minimum, maximum]. Both
     bands have 99 cases and nonzero IQR: band 2 IQR 2.0 (q25 −2.0, q75
     0.0), band 3 IQR 6.0 (q25 −2.0, q75 4.0)
     [cite: design_diagnostics.json | band_support.2, band_support.3 |
     n, iqr, q25, q75].
   - **Leverage passes.** Maximum row leverage **0.15486441040641785**
     against the frozen ≤ 0.20 bound [cite: design_diagnostics.json |
     maximum_row_leverage | value], at case sub-stroke0109, band 3, whose
     HU imbalance is −28.0 (Q1 median 30.0 HU, Q4 median 58.0 HU)
     [cite: per_row_design.csv | case_id=sub-stroke0109, stratum=3 |
     hu_imbalance, q1_median_hu, q4_median_hu, leverage]. The ten
     highest-leverage rows span 9 distinct patients (≥ 5 required)
     [cite: design_diagnostics.json | top_10_distinct_patients | value].
   - **Leave-one-patient-out stability passes on all three axes.** Across
     all 99 single-patient deletions — recomputing pooled centering and
     diagnostic scaling within each deletion — every matrix remains rank 3
     [cite: design_diagnostics.json | gates | all_loo_rank_3]; the
     condition number stays within 20.042406826639716 (deleting
     sub-stroke0094) to 20.325983967379745 (deleting sub-stroke0147)
     [cite: design_diagnostics.json | leave_one_patient_out_condition_min,
     leave_one_patient_out_condition_max | value], never approaching the
     ≤ 30 bound; and the per-deletion maximum leverage stays within
     0.154871023519075 to 0.18137690505955997 (the latter when deleting
     sub-stroke0147), inside the ≤ 0.20 bound — the v2-added gate
     [cite: design_diagnostics.json |
     leave_one_patient_out_maximum_leverage_min,
     leave_one_patient_out_maximum_leverage_max | value].

Because every number above is a deterministic function of the two pinned
input files, and the leave-one-patient-out sweep bounds single-case
sensitivity for conditioning, rank, and leverage simultaneously, the
feasibility **pass is structural to the observed covariate geometry, not
an artifact of any single patient**: that is demonstrated, not suggested.

## Suggests

Inferences beyond the frozen gates; deterministic numbers, interpretive
step mine.

1. **The interaction column was the binding pathology of the v1 design.**
   On the same pinned inputs, the same 198-row split, and the same
   diagnostic convention, removing the band-by-imbalance interaction moved
   the condition number from 38.889769743817595
   [cite: probes/045/results/results_v2/design_diagnostics.json |
   condition_number | value] to 20.222895326167112, and maximum leverage
   from 0.26358236965333054
   [cite: probes/045/results/results_v2/design_diagnostics.json |
   maximum_row_leverage | value] to 0.15486441040641785 — both from
   failing to comfortably passing. This supports (does not prove) the v1
   interpretation's diagnosis that near-collinearity of the interaction
   with its parent columns under compressed band-2 support drove the v1
   failure.

2. **Band-2 exposure support remains compressed; the pooled design
   absorbs it by construction, not by curing it.** Band 2 still lands on
   17 distinct imbalance values with IQR 2.0
   [cite: design_diagnostics.json | band_support.2 | distinct_values,
   iqr] — identical to the v1 geometry — while band 3 has 26 and IQR 6.0
   [cite: design_diagnostics.json | band_support.3 | distinct_values,
   iqr]. The v2 contract deliberately replaced the per-band ≥ 20 rule
   with a pooled rule because the reduced model estimates one pooled
   slope; that is why this geometry now passes. Any future specification
   that re-introduces band-specific slopes re-inherits the v1 problem
   unchanged.

3. **Extreme-imbalance rows are well absorbed by the reduced design.**
   The v1 maximum-leverage driver (sub-stroke0183, band 2, imbalance
   +18.0) now carries leverage 0.07314570734779892
   [cite: per_row_design.csv | case_id=sub-stroke0183, stratum=2 |
   leverage]; the new maximum sits on the most negative imbalance row
   (sub-stroke0109, band 3, −28.0) at 0.15486441040641785, inside the
   frozen ≤ 0.20 bound. The tightest margin anywhere in the audit is the
   per-deletion leverage maximum 0.18137690505955997 (deleting
   sub-stroke0147, whose own band-3 imbalance is −27.0
   [cite: per_row_design.csv | case_id=sub-stroke0147, stratum=3 |
   hu_imbalance]) against the frozen ≤ 0.20 bound. A passed gate, but the
   outcome-analysis designer should know the influence budget is least
   slack there.

4. **Centering was nearly inert, again.** The pooled HU-imbalance mean is
   −0.15909079349402225 [cite: design_diagnostics.json |
   pooled_hu_imbalance_mean | value]; the pass, like the v1 failure, is a
   property of the exposure geometry, not of the centering rule.

## Does not establish

- **Anything about the association between HU imbalance and final-infarct
  contrast d.** Zero d values were read [cite: summary.json |
  outcome_values_read | value]; no slope, no adjusted contrast, no
  direction exists anywhere in this bundle.
- **That the common-slope restriction is scientifically appropriate.**
  The contract's own `risky_assumption_tested` clause states the probe
  "does not test whether the common-slope scientific restriction is
  true," and its open question for the human — whether one pooled slope
  preserves enough of the attribution question — is a scientific-model
  judgment no feasibility pass can answer. The v1 interaction design was
  the more direct operationalization of "does imbalance account for the
  *band-specific* reversal"; the pooled reduction buys conditioning at
  the price of that directness, and only the human can price it.
- **Anything about whether tissue composition explains, contributes to,
  or fails to explain idea-023's band-2/band-3 reversal.**
- **Anything about median NCCT attenuation as a viability or tissue-type
  measurement**, or about any model's use of any signal.
- **That the eventual outcome analysis will be informative.** Geometric
  feasibility bounds numerical behavior, not scientific power or effect
  size.

## Validity failures

None. No invalidating-failure clause fired: no outcome-access breach (0
values read, 0 reserved cases), no input-identity failure (both sha256
pins recorded and matching the contract's frozen values), no join failure
(99/99 per band, no duplicates, no reserved case encountered), no
nonfinite value (the degenerate-geometry refusal path never triggered),
no analysis deviation (one variant, band 1 excluded, no interaction
column, thresholds byte-identical to the approved contract per the in-run
literal-drift guard), no lineage failure (the v1 bundle at
`results_v2/` is untouched; this run wrote a separate `results_v3`
directory from a fresh output root [cite: resolved_config.json |
output_dir | value]), no missing required output (all eight
contract-required artifacts present, plus determinism and split
manifests and `exclusions.csv`). This is a **valid positive**, not a
lucky run.

## Findings, stated positively and negatively

- **Positive finding (the result):** the frozen three-column pooled-slope
  design passes every one of the ten recorded feasibility gates —
  conditioning (20.22 vs ≤ 30), rank (3), band counts (99/99), band IQR
  (2.0 / 6.0), pooled distinct support (29 vs ≥ 20), leverage (0.1549 vs
  ≤ 0.20), influence spread (9 distinct patients in the top ten), and
  full leave-one-patient-out stability of rank, conditioning, and
  leverage. Under the contract's pre-registered classification this
  **supports drafting a separate outcome-analysis contract for this one
  common-slope operationalization** — and only that.
- **Negative findings:** none from this run. The descriptive residual
  worth carrying forward is band 2's unchanged compressed support (17
  distinct values, IQR 2.0), which the pooled design tolerates but does
  not repair.

## Authorized variants

One variant was authorized (`maximum_variants: 1`) and exactly one was
run: the approved real-input pooled-slope design audit, seed 0, smoke off
[cite: run_log.txt | phase 1 | line 2; cite: summary.json | smoke |
value]. No other variant, seed, threshold, or transform was executed. The
executed v1 interaction audit is a separate, completed historical
contract (blob `e7071541…`, its own bundle and decision), not a variant
of this one; the contract's scope clause expressly forbade re-running it
here, and it was not re-run. (The separate `probes/045/verification.json`
receipt records the pre-approval harness self-check of
2026-09-01T05:47:02Z; it is a code-review artifact, not a scientific
variant.)

## Next decision

**ADVANCE.** The contract's interpretation clause prescribes the
consequence of a pass: it "supports drafting a separate outcome-analysis
contract for this one common-slope operationalization." Concretely:

1. Draft the outcome-analysis contract through probe-plan: the
   prespecified pooled-slope fit of d on band + centered HU imbalance
   over these same 198 frozen rows, with the card's equal-patient-weight
   estimator and patient-bootstrap machinery, frozen interpretation rules
   (including the card's sensitivity-limited-null classification from the
   debate concession), and fresh human approval.
2. At that approval the human must answer the contract's standing open
   question — whether one pooled HU-imbalance slope preserves enough of
   the band-specific attribution question to be worth reading d for. A
   pooled slope cannot, by construction, show band-2 and band-3
   imbalance acting in opposite directions; if the human judges that
   band-specificity is essential, the honest alternative is a redesigned
   band-specific specification that first solves the v1 conditioning
   problem, not a silent fallback to this one.
3. Under THIS contract, read nothing further: its stopping rule was
   honored ("do not proceed to outcome analysis regardless of result")
   and its authority is spent. The 49 reserved cases and all observed d
   values remain unread [cite: summary.json | reserved_cases_accessed,
   outcome_values_read | values].

The scientific question of idea 045 — whether attenuation imbalance
accounts for the parent reversal — is neither supported nor weakened by
this result. What changed is that a numerically sound, pre-registered
instrument for asking it now exists and awaits the human's judgment on
whether it asks enough of the question.
