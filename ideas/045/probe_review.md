# Probe code review — idea 045, contract v2 (pooled-slope), round 1

Artifacts reviewed: `probes/045/run.py` (committed f7aec67, sha256
`9733732cb005e6ca5bce6d4f03c53272ddaae24d8a9fbf9099f956ee3e645555`, computed
during this review), `probes/045/requirements.txt`, `probes/045/README.md`,
`probes/045/verification.json`, against `ideas/045/probe_contract.yaml` v2
(blob `5615afea1e2f8309745a2d6558bd9118e5e9f1f3`, verified this round equal to
both the `HUMAN_APPROVED_PROBE` marker binding and the working-tree contract
file) and `ideas/045/feasibility.md`. There is no `contract_requirements.md`
in `ideas/045/`, so criterion 5's requirements-governed checks do not apply.

This is the first review of the v2 probe. The v2 code is a scoped diff of the
executed, previously APPROVED v1 probe (diff a5ec5db → f7aec67 read in full);
the review re-checks the complete standards checklist and contract fidelity on
the whole file, with particular attention to every changed region.

Method note: this environment blocks process execution, so the smoke run could
not be re-executed here. Smoke evidence is the committed harness receipt
(`verification.json` at f7aec67: `py_compile` pass and `--smoke` exit 0 into a
throwaway directory, checked 2026-09-01T05:39:26Z, nine seconds before the
commit that carries both it and the exact reviewed `run.py` — tree-bound by
construction) plus line-level reading, the same basis as prior rounds.
Real-data identities and counts cited below were re-derived directly from the
two input CSVs during this review; no gated quantity (imbalance distribution,
conditioning, leverage) was computed, preserving the probe's deliverables.

## Contract fidelity — verified

**Approval gate.** `verify_approval` (run.py:121-141) requires the marker and
contract, extracts `contract_blob`, recomputes the git blob of the live
contract, and refuses on mismatch (exit 2). The literal-drift guard
(run.py:133-140) was updated to the v2 wording; all seven literals
(`contract_version: 2`, variant/GPU/seed caps, `condition number <=30`,
`maximum row leverage <=0.20`, `pooled exposure has at least 20 distinct`)
were grep-confirmed present in the approved contract during this review.

**Primary metric.** `condition_number` (run.py:300-314) scales only
non-intercept columns to unit L2 norm, solely for the diagnostic, exactly as
the contract's primary_metric clause specifies; the metric chain
(SVD → σ₁/σₙ) is unchanged from the executed v1 convention the contract's
baselines section inherits.

**The v2 model change is exact.** The design matrix is precisely the three
frozen columns — intercept, band-3 indicator, pooled-mean-centered
HU imbalance — with the interaction removed (run.py:321-324, shape asserted
(n, 3)). Centering is computed once over all rows at the pooled mean
(run.py:319-320), with no scaling, trimming, winsorization, ranking, binning,
or alternative centering anywhere. The per-row output drops the v1
`interaction` column (run.py:531-533).

**All nine positive_rule clauses map onto the gates dict one-to-one**
(run.py:380-393), with the compound leave-one-out clause split into three
explicit gates: `rank_3`; `condition_number_le_30`; `each_band_99_cases`;
`each_band_nonzero_iqr`; `pooled_at_least_20_distinct` (the v2 pooled rule,
correctly replacing v1's per-band rule); `maximum_leverage_le_0_20`;
`top_10_include_at_least_5_patients`; `all_loo_rank_3`;
`all_loo_condition_le_30`; and the new `all_loo_maximum_leverage_le_0_20`
implementing v2's added per-deletion max-leverage requirement
(run.py:367-372, 390-392). Leave-one-patient-out recomputes pooled centering
and diagnostic scaling within each deletion (run.py:358-366), as the
secondary-metrics clause demands, and now also records the per-deletion
leverage range in diagnostics (run.py:405-406).

**Secondary metrics complete.** Rank and all three singular values; pooled
**and** band-specific min/max/median/q25/q75/IQR/distinct/count (band:
run.py:333-344; pooled — new in v2, matching the contract's pooled support
clause: run.py:345-353); per-row hat leverage, maximum, and top-ten distinct
patients; complete LOO table.

**Outcome blindness unchanged and intact.** `load_keys_without_outcomes`
(run.py:212-249) checks the exact five-column header (confirming `d` exists
per `forbidden_column_values`), validates the field count by delimiter
counting, and consumes only the substrings before the second comma; the
remainder is never sliced, split, parsed, or retained. The split manifest is
written and hashed (run.py:191-193, called at 473) before the outcome-bearing
file is first opened (480). The smoke fixture writes a non-numeric sentinel
into `d` (run.py:455-458), so any future regression that parses the field
crashes the harness check.

**Caps and stopping rule.** One variant (single linear pass, logged
`Variant 1/1`, run.py:443), one seed (constant 0, seeded though no draw
exists, per `randomness: None`), zero GPU, zero network (no network imports;
`network_calls: 0` recorded, run.py:560). The run stops after the single
design audit; no outcome analysis exists in the file.

**Required outputs.** All eight contract-required artifacts are written
(resolved_config.json 553-562, input_manifest.csv 501-511, exclusions.csv
490-493, per_row_design.csv 534, design_diagnostics.json 535, summary.json
539-552, environment.txt 563-568, run_log.txt 579), plus split and
determinism manifests. `summary.json` carries no `phase` field, which is
correct under the S2b ruling (phase optional under declared interfaces).

**Lineage.** Nothing reads or writes the v1 bundle: default inputs are the
two idea-023 tables, and every output self-identifies as
`contract_version: 2` with the v2 blob in `resolved_config.json`. See
non-blocking finding 2 for the operational residual.

**Input identities re-verified on disk.** `bin_tissue_audit.csv` sha256
`35e896df…` and `per_patient.csv` sha256 `1d01551c…` both match the
contract's frozen_inputs exactly; headers match the frozen literals; 594
audit data rows (297 Q1_low_CBV + 297 Q4_high_CBV; 198 per stratum 1/2/3)
and 297 key rows (99 per stratum, zero duplicate case-stratum keys). Expected
real-run accounting is therefore audit 594 = 396 selected + 198 filtered,
keys 297 = 198 + 99, `excluded_input_rows` 297 in 2 aggregate records —
identical shape to the executed v1 bundle.

## Standards checklist — all six MET

1. **Determinism manifests** — start written and printed before measurement
   (run.py:497-513); end recomputed including re-hashing both input files,
   compared for exact equality with classified exit 7 (run.py:570-577).
2. **Exclusions log with reasons** — band-filter drops recorded as counted
   aggregate records with reason `non_primary_band` (run.py:482-494);
   totals in summary, manifests, and log line.
3. **Assertion per transform** — conservation asserts on both loaders
   (180, 248), band membership (179, 247), style containment (265), triple
   key equality (294-295), row count (296), matrix shape/finiteness
   (324-325), leverage shape/finiteness/range (329-331), pooled-support
   count (353), LOO shape/finiteness/count (368-369, 373).
4. **Declared state, no hidden state or network** — constants with contract
   provenance (41-57); seeds set (434-435); no network access anywhere.
5. **Split-before-outcome** — split_manifest.csv written and sha256-hashed
   in phase 1 (473) before per_patient.csv is opened in phase 2 (480). In
   smoke mode the fixture is *written* earlier, but the split still precedes
   the only *read*.
6. **Smoke** — harness receipt shows exit 0 within the verifier's bounds
   (the materially identical v1 workload measured 264 ms); structurally
   unable to satisfy the contractual gate twice over: `contractual_pass`
   requires `not args.smoke` (537), and the 24-case smoke geometry can never
   satisfy `each_band_99_cases` (383, which demands 99).

## Silent-failure surfaces — improved over v1

Two v1 non-blocking findings are affirmatively closed by this diff:

- **Degenerate geometry now fails loudly.** The v1 path returned
  `float("inf")` (serialized as non-strict bare `Infinity`); v2 refuses with
  classified exit 6 on a zero-norm column, a nonpositive trailing singular
  value, or a nonfinite condition number (run.py:304-313), matching the
  contract's value-failure clause — nonfinite is an invalidating failure,
  never a NEGATIVE_PATTERN.
- **Unknown style is now schema drift, not an exclusion.** A primary-band
  row with an unrecognized `style_group` hard-fails EXIT_JOIN naming the row
  (run.py:257-258) — exactly the defense-in-depth the v1 round-2 review
  recommended; the v1 unknown-style split-manifest corner is gone (the split
  is written first, but the run then refuses before any gate is computed).

The v1 round-2 protections are retained: bidirectional join equality with
named offending keys in both directions (run.py:269-275), per-case Q1/Q4
cell completeness (285-286), duplicate refusal on both sides (241-242,
260-261), and complete filtered-row accounting reconstructible from the
bundle alone. Missing files, empty files, and wrong headers all refuse with
classified exits; no try/except swallows anything (the only handler is the
top-level classifier, which prints the full traceback for unexpected faults,
run.py:594-604).

## Claim discipline — clean

Status vocabulary is exactly `POSITIVE_PATTERN` / `NEGATIVE_PATTERN` /
`SMOKE_ONLY` (538), and both printed interpretation templates (583-590) track
the v2 contract's pattern language, including the corrected negative
consequence — "requires a new contract before any further variant" — and the
mandatory "not evidence against tissue composition or the parent
association" scope guard. No stronger sentence appears anywhere in the file.
No outcome value, reserved case, or additional analysis is reachable.

## Readability — good

Accurate module docstring updated to the three-column model with exit-code
table (2-22); four narrated phase comments; thresholds annotated with
contract provenance (46-48); per-band, pooled, and headline progress lines;
plain-English interpretation template at the end. The human can run it from
the README's one-line command.

## Non-blocking findings

1. **Input pins are recorded, not enforced in-run.** run.py hashes both
   inputs into the manifests but never compares them to the contract's
   frozen_inputs values, so a `--audit-csv`/`--keys-csv` override would run
   to completion on wrong inputs. The drift is fully evident from the bundle
   (recorded sha256 vs contract pins) and the interpret/import stages check
   exactly that — this is the pattern the executed v1 established — and the
   `test`/`reserv` path refusal (467-469) blocks the dangerous direction.
   Defense-in-depth for a future revision: refuse with EXIT_INPUT when a
   computed input hash differs from the contract's frozen value (the
   contract text is already read for the literal-drift guard).
2. **No output-directory collision guard.** `--output-dir` is
   `mkdir(exist_ok=True)` then overwritten (436); pointing it at the v1
   `results/results_v2` directory would modify v1 artifacts — the contract's
   lineage-failure clause makes that run invalid, but the code does not
   refuse it. Mitigated by the driver's blob-scoped output-directory policy
   and git; a refusal when the target already contains a `summary.json`
   would close it.
3. **`run_log.txt` written on the success path only** (579; carried from
   v1). Failures still persist forensics via stderr traceback (601-603).
4. **Decorative reserved-case assert.** `reserved_cases = set()` is
   hardcoded empty (206), so the disjointness assert (207) can never fire;
   the real guarantee is that the hash-pinned inputs physically lack
   reserved cases. The comment says so; the assert adds no protection.
5. **Exit-taxonomy quibbles** (carried class): nonnumeric `stratum`/
   `median_hu` in the audit exits 6 (value/design, 172) though it is input
   schema drift; nonnumeric stratum in the keys file exits 5 (238).
   Fail-loud in every case; wrong label only.
6. **Verification receipt is the thin harness format.** The committed
   `verification.json` records compile + smoke pass but no `run_py_sha256`
   or named regression booleans (the rich v1 round-2 file was one-time
   agent-authored review evidence, later overwritten by the standard
   verifier). Tree-binding via commit f7aec67 (checked nine seconds before
   commit) is adequate; noting the weaker form for the record.
7. **Cosmetics:** `build_design`'s `exclusions` return is now always empty
   (unknown style refuses instead of excluding) — vestigial parameter;
   smoke-branch `keys_total_rows`/`keys_filtered_rows` assignments (461-462)
   are overwritten by the real loader call at 480 (carried); `environment.txt`
   contains JSON despite its extension (carried; the contract names the
   file).

## Verdict

The diff from the executed v1 probe is exactly the approved v2 respec —
interaction column removed, pooled distinct-support gate, per-deletion LOO
max-leverage gate, pooled support diagnostics, updated literal guard and
claim text — plus two genuine hardening improvements (loud degenerate
geometry, unknown-style refusal), with no scope, threshold, estimand, or
output change beyond the contract and no new silent-failure surface. Caps,
stopping rule, outcome blindness, and claim language are contract-faithful;
all six hard standards are met; input identities and structure re-verified
on disk against the frozen pins.

```json
{"verdict": "APPROVE", "blocking": [], "note": "v2 diff implements exactly the approved pooled-slope respec (rank-3 design, pooled distinct gate, LOO leverage gate) and closes two v1 findings; no scope or threshold drift, all standards met, inputs re-verified against frozen pins."}
```
