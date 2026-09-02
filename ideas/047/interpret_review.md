# Interpret review — idea 047, Phase A (cross-family checker)

Reviewing family: Claude. Document under review:
`ideas/047/interpretation.md` (round 1). Results bundle:
`probes/047/results/results_v2/` at commit
`6037f24122766fe1c68f16eb9f38d9a16c2c5e66` (verified: that commit
introduces exactly the 17 bundle files plus the import receipt).
Governing contract blob `b4887c05a21bfe870589b5d9982066943df679d5`
(corroborated in `resolved_config.json:contract_blob` and
`ideas/047/state.json` approval, stale=false).

Note on check 2's inherited wording: the stage checklist's "tier 2 /
vendor scope / anchor exclusion / baseline-not-floor" items are 004-era
specifics. Their 047 analogs, applied here: no threshold/margin/verdict
language in the support clause; finite-population scope and the two
bookkeeping exclusions stated wherever counts appear; the reversal-
accounting share never read as contribution per unit support; and the
deterministic-probe uncertainty constraint (uncertainty located in case
selection and scope, not seeds).

## Check 1 — Citations resolve (transcription-exact)

Every `[cite: ...]` tag was opened and resolved against the bundle.
All pass. Enumerated:

1. `support_shares.json | sole_disproportionality_comparison |
   head_abs_contribution_share,head_support_share` — file holds
   0.5063509495830807 and 0.08961200117675944. Layer A's
   "50.63509495830807%" and "8.961200117675944%" are exact digit-shift
   conversions; Layer C row 1 quotes the raw fractions verbatim. PASS.
2. `support_shares.json | descriptive_displays |
   spearman_rho_abs_contribution_vs_support` — 0.07085961657390227,
   quoted verbatim in Layer A, the Suggests row, and the
   negative-finding row. Independently recomputed by this reviewer from
   the file's own `rank_discrepancy_sum_d_squared` = 150242:
   1 − 6·150242/(99·(99²−1)) = 1 − 901452/970200 =
   0.07085961657390227. PASS.
3. `support_shares.json | reversal_accounting |
   signed_head_net_gap_share[,label]` — 0.7928912778985707
   ("79.28912778985707%"), with the `label` field stating exactly the
   after-cancellation / not-per-unit-support restriction the
   interpretation paraphrases. PASS.
4. `summary.json | clinical_minimum_set_supported=true,
   phenotype_rows_opened=0` — both present with those values. PASS.
5. `resolved_config.json | contract_blob=b4887c05...,
   contract_version=2,variants=1,gpu_minutes=0,seed=20260902` — all
   five fields present with exactly those values. PASS.
6. `determinism_manifest_end.json | row_counts.exclusions.csv=101,
   row_counts.per_case_contributions.csv=99` — exact. The narrative
   claim "hashed at the start and end; the recorded manifests agree"
   was verified directly: `diff determinism_manifest_start.json
   determinism_manifest_end.json` is empty, and the manifests cover
   the three frozen tables, take-13 source, and dictionary. PASS.
7. `provenance_gate.json | analyzed_rows=99,bookkeeping_rows,
   unique_analyzed_ids=true,id_set_matches_contribution_table=true` —
   all exact; `bookkeeping_rows` names sub-stroke0142
   (excluded_archive_lesion) and sub-stroke0043 (excluded_case,
   source_corrupt_member), matching the CONSORT sentence. PASS.
8. `summary.json | reserved_cases_accessed=0,phenotype_rows_opened=0`
   — exact. PASS.
9. `provenance_gate.json | b_finite_positive_integer_count=99,
   b_min=1401,b_max=617540,discrepancies=[]` — exact; min/max
   independently confirmed from `per_case_support.csv` column 6
   (sorted: 1401 … 617540). PASS.
10. `provenance_gate.json | census_cross_checks.sign_counts.positive=54,
    zero=6,negative=39,census_cross_checks.checks` — exact; all seven
    check booleans true. The pinned values were additionally re-read
    from the frozen `probes/046/results/results_v3/census_summary.json`
    (top_k 10 absolute_mass_share 0.5063509495830807,
    signed_head_net_gap_share 0.7928912778985707, sign counts 54/6/39).
    PASS.
11. `provenance_gate.json | pass=true,discrepancies=[]` — exact (used
    in three places). PASS.
12. `support_shares.json | sole_disproportionality_comparison |
    head_abs_contribution_sum,total_abs_contribution_sum,
    head_support_voxels,total_support_voxels,...` —
    0.04367036086720666, 0.08624524334982282, 2025630, 22604450, all
    quoted exactly. Reviewer recomputation: summing the ten
    `in_head=True` rows of `per_case_support.csv` by hand reproduces
    2,025,630 voxels and 0.04367036086720666 exactly; the share
    quotients are consistent. PASS.
13. `proposed_variable_freeze.json | dictionary.bytes=12149,
    dictionary.md5=c8d806a021614c6bb9f732756f9701d4` — exact, and the
    staged xlsx in the bundle is 12,149 bytes per the commit stat. PASS.
14. `summary.json | dictionary_cells_inventoried=148` — exact
    (consistent with the 149-line dictionary_inventory.csv incl.
    header). PASS.
15. `proposed_variable_freeze.json | constructs,center.documented=false`
    — constructs mrs_3month, nihss_24h, nihss_admission, age, sex all
    `matched: true` with verbatim dictionary rows; `center.documented:
    false` with empty matches; `minimum_set.supported: true`. The
    interpretation's "proposed bindings, not analyzed clinical
    variables" framing matches the file's own binding_note. PASS.
16. `summary.json | status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT,
    wall_seconds=0.013` — exact. PASS.
17. `summary.json | phenotype_rows_opened=0,analyzed_cases=99` (Layer C
    does-not-establish row) — exact. PASS.

Uncited-quantitative-claim scan: every number outside the result-card
identity block carries a cite. Process facts (human approval of the
exact blob; probe review approved "after two rounds") verify against
`ideas/047/state.json` and `ideas/047/probe_review.md` (revision round
2, APPROVE). No unresolvable citation, no mis-transcription found.

## Check 2 — Claim bounds

- No threshold, cutoff, margin, interval, test, or is/is-not verdict
  appears anywhere in the support-clause prose; Layer A explicitly
  frames the share pair as "an exact descriptive concentration rather
  than a thresholded verdict," and Layer B item 5 states no interval,
  test, margin, or alternative subgroup was run (confirmed: none exists
  in the bundle). Grep for prohibited vocabulary ("clinically
  silent/marked", "keystone", "disproportionate", "significant",
  "p-value", "confidence interval") finds hits only inside the
  out-of-scope disclaimer and the idea title — negations, permitted.
- The Suggests-row phrasing "not simply proportional ... the share pair
  is widely separated" was scrutinized against the contract's
  interpretation_rule and round-3 freeze. It is an arithmetic
  comparison of the two exact shares, scoped with "realized," carries
  no generalization, and is demoted to Suggests with the stated reason
  (no case-level uncertainty machinery; outcome-selected head). Within
  bounds.
- The 79.29% signed share appears only under reversal-accounting
  language and is twice explicitly barred from a per-unit-support
  reading — matching the frozen label in the file. PASS.
- No aggregation appears that the analysis files do not themselves
  contain (shares, sums, rho, sign counts, min/max are all stored
  fields; nothing was pooled or averaged by the author).
- Scope and exclusions stated where counts appear: 99 analyzed of 101
  records, both bookkeeping rows named with reasons, zero reserved
  cases and zero phenotype rows, finite-population caveat in Layer A.
- Deterministic-probe uncertainty constraint: correctly applied. The
  Uncertainty location section places uncertainty in case selection and
  scope, not seeds, and correctly notes the fixed seed 20260902 is
  reserved for Phase-B relabelings (matches the contract's randomness
  clause). PASS.

## Check 3 — Completeness without cherry-picking

What I checked for, in the tables the interpretation draws on:

- `rank_discrepancy.csv` / `per_case_support.csv` (99 rows each,
  consistent head marks): the ten head cases are heterogeneous in
  support — eight have strongly negative rank discrepancies (−32 to
  −91), while sub-stroke0014 and sub-stroke0114 hold support ranks 1
  and 4 (the largest and fourth-largest eligible-support values in the
  whole cohort, 617,540 and 583,847 voxels; discrepancy +4 each). This
  is the closest thing to a complicating feature in the bundle. It does
  not contradict any stated claim: the interpretation's concentration
  claims are aggregate share arithmetic (exact regardless of within-
  head composition), it never asserts that head cases individually
  have small support, and the b_max=617540 the narrative quotes is in
  fact a head case. Omitting the casewise breakdown is legitimate
  selectivity, not suppression.
- Sign structure: the 39 opposing and 6 zero cases are reported (sign
  counts), and the cancellation caveat on the signed share is carried.
- `summary.json` and `provenance_gate.json` were scanned for any field
  contradicting the narrative (discrepancies, kill conditions, smoke
  flag, head_size): none exists; `discrepancies` is empty and
  `pass: true`.
- No stratum-reversal analog exists in this bundle (single cohort, one
  comparison); nothing material is omitted. PASS.

## Check 4 — Verdict separation

- Demonstrates rows are exclusively deterministic finite-population
  arithmetic under frozen inputs, or mechanically gated process facts —
  correct register for a deterministic probe.
- The proportionality reading is confined to Suggests with an explicit
  stated reason; the small rho is classified as a negative finding with
  the "not an inferential null / does not establish independence"
  guard.
- Does-not-establish rows correctly cover all clinical readings
  (phenotype_rows_opened=0) and the signed-share misreading.
- The terminal status is presented as successful completion of Phase A
  only, "not completion of the study," matching the contract's
  positive_pattern, and the Next decision advances only to the
  amendment gate, not Phase B. No exploratory statement is worded
  confirmatorily. PASS.

## Check 5 — Plain-language fidelity

`interpretation.md` contains no plain-summary section (headers: Result
card, Layer A–C, Uncertainty location, Next decision), so this check is
not applicable to the document under review. No hedge-dropping exists
anywhere in it.

## Verdict

All five checks pass. The interpretation is transcription-exact,
bounded within the contract's claim discipline, complete with respect
to the bundle's material content, and correctly separates demonstrated
arithmetic from suggested readings.

```json
{"verdict": "APPROVE"}
```
