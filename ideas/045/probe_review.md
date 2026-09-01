# Probe code review — idea 045, round 2

Artifacts reviewed: `probes/045/run.py` (committed a5ec5db, sha256
`8d685dd4847c2343ace4285d84d7f17e18de386dceed4c769576d40ce0817107`, matching
`verification.json`), `probes/045/requirements.txt`, `probes/045/README.md`,
`probes/045/verification.json`, against `ideas/045/probe_contract.yaml` v1 (blob
`e7071541036a17f4a02ec264693209fec5c1337d`; re-verified this round against both
`HUMAN_APPROVED_PROBE` and the working-tree contract file) and
`ideas/045/feasibility.md`. There is still no `contract_requirements.md` in
`ideas/045/`, so criterion 5's requirements-governed checks do not apply.

This round verifies the two round-1 blocking findings (B1, B2; review of
2026-09-01, preserved in git at 2a56f99) against the revised code, and re-checks
the full standards checklist and contract fidelity on the round-2 diff.
Judgment is on the artifact's content only. Method note: this environment
cannot execute the probe, so smoke evidence comes from `verification.json`
(sha-bound to the exact reviewed file) plus line-level reading, the same basis
as round 1; real-data row/style counts cited below were re-derived directly
from the two input CSVs during this review.

## Round-1 blocking findings — both RESOLVED

### B1 (join gate one-directional) — FIXED as specified

The round-1 minimal remedy is implemented verbatim in `build_design`
(run.py:266-274): after the audit cells are built, `audit_keys` is derived as
the set of `(case_id, band)` pairs present on the audit side, and any inequality
with `outcome_keys` fails `EXIT_JOIN`, naming a bounded sample (10) of the
offending keys in **both** directions (`audit_only_sample`,
`outcome_only_sample`). Consequences verified:

- The round-1 concrete failure path is now refused: an audit input carrying a
  100th (e.g. reserved) case in a primary band with Q1/Q4 rows produces
  `audit_keys ⊋ outcome_keys` → `EXIT_JOIN` before any design row is built, so
  no gate can be satisfied and no summary is written. The split manifest is
  still written first, which is the correct order — the split freeze must
  precede outcome-file access; the refusal lands at the join.
- The formerly vacuous set-equality check is gone; in its place run.py:294
  asserts `expected_keys == outcome_keys == audit_keys`, which is now an honest
  by-construction invariant chained to the real gate at line 269 rather than a
  check masquerading as protection.
- The 99-count is now effectively enforced on both sides: the outcome side is
  counted per band (run.py:279-280), and set equality transfers that count to
  the audit side.
- The per-case missing-cell path is still independently covered: a case with a
  Q1 row but no Q4 row passes the key equality yet fails at run.py:284-285.
- Harness regressions exist for exactly this fix:
  `audit_only_key_exits_with_join_failure: true` and
  `bidirectional_join_sets_are_equal_before_design: true` in
  `verification.json`.

One narrow residual corner survives, recorded below as non-blocking finding 4
because it is no longer silent.

### B2 (unaccounted band-filter drops) — FIXED

- `load_audit` (run.py:159-181) and `load_keys_without_outcomes`
  (run.py:214-246) now count total versus filtered rows, each with a
  conservation assertion (`total == selected + filtered`, lines 180 and 245).
- The band-filter drops become explicit exclusion records with reason
  `non_primary_band` and a count (run.py:457-464); `exclusions.csv` gains a
  `count` column (466-468); the aggregate `excluded_input_rows` is computed
  (469), logged, and written to the summary.
- File totals are now everywhere the round-1 finding demanded: `total_rows` per
  input in both determinism manifests (run.py:393-399), in
  `input_manifest.csv` (484-486), and in `summary.json` as
  `audit_total_rows` / `audit_selected_rows` / `keys_total_rows` /
  `keys_selected_rows` plus `exclusion_records` and `excluded_input_rows`
  (519-521).
- Arithmetic checked against the real inputs (re-verified during this review:
  594 audit data rows, exactly 297 `Q1_low_CBV` + 297 `Q4_high_CBV`; 99
  per_patient rows in each of strata 1/2/3): audit 594 = 396 selected + 198
  filtered; keys 297 = 198 selected + 99 filtered; `excluded_input_rows` will
  read 297. The drop is now fully reconstructible from the bundle alone,
  which is what the standard requires.
- Harness regressions: `band_filter_row_accounting_is_complete: true` and
  `row_totals_present_in_manifests_and_summary: true`.

## Standards checklist verification

1. **Determinism manifests — MET.** Start manifest written and printed before
   measurement (run.py:472-488), end manifest recomputed (re-hashing inputs,
   catching mid-run mutation) and compared for exact equality with classified
   exit 7 (546-548). The new `total_rows` fields appear identically in both.
2. **Exclusions log — MET** (was the B2 blocker). Reasons and counts per
   record; totals surfaced in summary and log line (470).
3. **Assertion per transform — MET.** Row-conservation asserts on both loaders
   (180, 245), band membership (179, 244), non-empty split bands (186), style
   containment (264), triple key equality (294), row count (295), matrix
   shape/finiteness (318-319), leverage shape/finiteness/range (323-325), LOO
   count (353).
4. **Declared state — MET.** Seeds and thresholds are top-level constants with
   contract provenance (41-50); no network imports; `network_calls: 0`.
5. **Split-before-outcome — MET.** `split_manifest.csv` written and hashed
   (191-193) in phase 1, before `per_patient.csv` is first opened in phase 2
   (455); harness confirms `split_manifest_written_before_keys_file_open`.
   With B1 fixed, the split's content is now also protected: a phantom primary-
   band Q1/Q4 case in the audit can no longer survive to completion.
6. **Smoke — MET.** 264 ms per `verification.json`, always `SMOKE_ONLY`,
   `contractual_pass` requires `not args.smoke` (510) on top of the
   structurally unsatisfiable 99-case gate; the `d`-field sentinel self-test is
   retained (432).

## Contract fidelity — re-verified on the round-2 diff

The diff between 527271d and a5ec5db touches only join validation, row
accounting, and manifest/summary bookkeeping. Estimand, thresholds, metric
chain, and outputs are byte-untouched: frozen constants (46-50) and the
approval-time literal-drift guard (133-140) unchanged; primary condition-number
chain, band support, leverage, and LOO diagnostics unchanged (299-385); all
nine `positive_rule` clauses still map one-to-one onto the `gates` dict
(361-371); outcome blindness path unchanged (209-246 — fields 0 and 1 only,
remainder never sliced or retained); caps unchanged (one variant, one seed,
zero GPU, no network); claim language unchanged and no stronger sentence
appears (556-563). All seven contract-required outputs are written; the only
output-schema change is the `count` column and totals described under B2,
which the contract's output-integrity clause permits and the standards demand.
Approval gate re-verified live: marker blob equals the current contract blob
(`e7071541…`).

## Non-blocking findings

1. **Degenerate-geometry path emits non-strict JSON** (carried from round 1,
   unchanged): zero column norm or zero trailing singular value yields
   `float("inf")` (run.py:304, 308), serialized by `json.dumps` as bare
   `Infinity`, and an empty `singular_values` list in the norm-zero branch.
   Gates fail in every such case, so no wrong positive is possible.
2. **Empty-band taxonomy** (carried, unchanged): a primary band absent from the
   audit surfaces as `AssertionError` → exit 12 (186) rather than a classified
   input failure. Fail-loud, wrong label only.
3. **`run_log.txt` written on the success path only** (carried, unchanged,
   552); tracebacks still go to stderr on failure (575-577), so forensics
   survive via console.
4. **Unknown-style split-manifest corner** (successor to round-1 finding 4,
   downgraded by the B1 fix): a case appearing in a primary band only under an
   unrecognized `style_group` is excluded from `cells` (255-257) and therefore
   from `audit_keys`, so it evades the key-equality gate while still being
   listed as `opened_census` in `split_manifest.csv` (the split derives from
   style-unfiltered rows, 184-190). This is no longer silent — the case is
   named in `exclusions.csv` with reason `non_primary_style_group` and shows up
   as a nonzero `exclusion_records` in the summary — and it cannot enter the
   analysis; the real audit contains exactly the two permitted styles.
   Defense-in-depth would treat an unknown style value as `EXIT_INPUT` schema
   drift instead of an exclusion; not required by the contract's row gate.
5. **`numpy==2.5.2` pin still unrecorded in `verification.json`** (carried);
   the real run's `environment.txt` (538) settles it, and a wrong pin fails
   loudly at install.
6. **Smoke-branch dead stores**: `keys_total_rows` / `keys_filtered_rows` set
   at 436-437 are overwritten by the real loader call at 455 (which reads the
   synthetic file). Harmless and cosmetically confusing only; the
   audit-side values at 434-435 are genuinely used.
7. **Type mixing in aggregate exclusion rows**: the `stratum` column carries
   the string `outside_primary` for the two aggregate records (458, 462)
   alongside numeric strata in per-row records. The `case_id: "*"` marker makes
   them unambiguous; cosmetic.

## Verdict

Both round-1 blockers are fixed exactly as specified — the bidirectional join
refusal with named offending keys, and complete filtered-row accounting
reconstructible from the bundle — each with a dedicated harness regression.
The diff introduced no scope, threshold, or estimand change and no new
silent-failure surface. The remaining findings are minor and none can produce
a wrong positive or an unaccounted drop.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Round-1 blockers B1 (bidirectional join gate, EXIT_JOIN with named keys) and B2 (band-filter accounting with totals in manifests/summary) verified fixed with harness regressions; diff is scope-clean and no new blocking finding exists."}
```
