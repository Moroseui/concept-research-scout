# Probe code review — idea 045, round 1

Artifacts reviewed: `probes/045/run.py` (committed 527271d), `probes/045/requirements.txt`,
`probes/045/README.md`, `probes/045/verification.json`, against
`ideas/045/probe_contract.yaml` v1 (blob `e7071541036a17f4a02ec264693209fec5c1337d`,
matching `HUMAN_APPROVED_PROBE`; blob re-verified against the working tree during this
review) and `ideas/045/feasibility.md`. There is no `contract_requirements.md` in
`ideas/045/`, so criterion 5's requirements-governed checks do not apply.

Judgment is on the artifact's content only.

## BLOCKING findings

### B1 — The join gate is enforced in one direction only; unmatched audit-side keys are silently ignored and pollute the split manifest (rules 1 and 2)

The contract's `row_gate` requires "exactly one Q1_low_CBV and one Q4_high_CBV audit row
for each case-stratum and exactly one matching per_patient key, with 99 unique cases in
each of strata 2 and 3. Reject duplicate or unmatched keys." Its `invalidating_failures`
name "unmatched case-stratum keys" and "any reserved/non-census case is encountered" as
join failures.

The implementation enforces only the outcome→audit direction:

- `build_design` (run.py:255-263) iterates over `band_cases` drawn from `outcome_keys`
  (per_patient side) and fails on a missing Q1/Q4 audit cell. Correct.
- The reverse direction is absent: an audit `(case, stratum)` present in `cells`
  (run.py:237-251) but missing from `outcome_keys` is never compared against anything.
  It is not failed, not counted, and not written to `exclusions.csv`.
- The check at run.py:271-273 (`expected_keys != outcome_keys`) is vacuous:
  `design_rows` is constructed by iterating over `outcome_keys`, so `expected_keys`
  equals `outcome_keys` by construction and the branch can never fire. It reads as the
  bidirectional join check the contract requires while providing no protection.
- Worse, `write_split_before_outcome` (run.py:179-200) derives the frozen split from
  the **audit** file's cases. A phantom or reserved case present in the audit input
  would be committed to `split_manifest.csv` as `"opened_census"`, hashed into the
  determinism manifests, and the run would still complete — potentially
  `POSITIVE_PATTERN` — with `reserved_cases_accessed: 0` asserted in three artifacts.
- The audit-side unique-case count is never checked against 99 anywhere; the only
  99-count check (run.py:257-258) is on the per_patient side.

Concrete failure path: point `--audit-csv` at a stale or wrong bundle file containing
100 cases in band 2 (one of them reserved). The run completes, the split manifest
claims 100 opened-census cases, no gate fires, and the summary asserts zero reserved
access. This is exactly the "prints a number on broken input" class, and it is the
failure class the contract's join clause exists to reject. The 023 arc's history
(census exit-5, take-9 cache guard) is precedent that wrong-input defense belongs in
the probe, not in operator care.

**Minimal remedy (no scope change):** after building `cells` in `build_design`, derive
`audit_keys = {(case, band) for (case, band, style) in cells}` and fail `EXIT_JOIN` if
`audit_keys != outcome_keys`, naming a bounded sample of the offending keys in the
message. This single set-equality makes the vacuous check real, enforces the 99-count
on both sides (the outcome side is already counted), and closes the reserved-case
path through defaults. Optional hardening, consistent with the contract's
input-identity clause: pin the two default inputs to the SHA-256s recorded in
`feasibility.md` (`35e896df…`, `1d01551c…`) and refuse on mismatch; recording alone is
what the contract's letter requires, so this part is suggested, not demanded.

### B2 — Dropped rows leave no exclusion record (standards checklist item 2)

Standard item 2: "every dropped case/row/voxel-group emits one line to an exclusions
file with the reason; totals appear in the summary."

On the real inputs, `load_audit` (run.py:170-171) silently drops all 198 band-1 audit
rows (594 file rows → 396 selected), and `load_keys_without_outcomes` (run.py:227-231)
silently skips all 99 band-1 per_patient keys. Neither drop produces an exclusion line
or a count: `exclusions.csv` captures only non-primary `style_group` values within
primary bands (run.py:241-245), of which the real file has zero, so the shipped
artifact set will show `exclusion_rows: 0` while a third of the input rows were
filtered. The manifests record only `selected_rows` (run.py:373-375), never the file's
total row count, so the drop is not reconstructible from the bundle at all — an
auditor must reopen the inputs to learn that 198 rows went missing.

Band-1 exclusion is contract-mandated scope (`split_policy`), so the *filtering* is
correct; the *accounting* is what is missing. **Remedy:** record the band-filtered
drops — either one aggregate exclusions line per input with reason
`non_primary_band` and a count, or per-row lines — and surface total-versus-selected
row counts in the manifest and summary. No analysis change.

## Standards checklist verification

1. **Determinism manifests — MET.** Start manifest written and printed before
   measurement (run.py:433-447), end manifest recomputed (re-hashing the inputs, so
   mid-run mutation is caught), compared for exact equality with a classified exit 7
   on mismatch, then written and printed (run.py:499-505).
2. **Exclusions log — UNMET.** Blocking finding B2.
3. **Assertion per transform — MET.** Band membership (174), non-empty split bands
   (180), style containment (252), row count (274), matrix shape/finiteness
   (297-298), leverage shape/finiteness/range (302-304), LOO count (332).
4. **Declared state — MET.** Seeds and thresholds are top-level constants annotated
   with contract provenance (41-50); paths are constants or CLI arguments; no
   network imports; `network_calls: 0` recorded.
5. **Split-before-outcome — MET.** `split_manifest.csv` is written and SHA-256-hashed
   (run.py:185-198) in phase 1, before `per_patient.csv` is first opened in phase 2
   (run.py:427); independently confirmed by the harness check
   `split_manifest_written_before_keys_file_open: true`. (But see B1: the split's
   *content* is derived from the unvalidated audit side.)
6. **Smoke — MET.** `--smoke` accepts `--output-dir`, ran in 266 ms per
   `verification.json`, always reports `SMOKE_ONLY`, and `contractual_pass` requires
   `not args.smoke` (run.py:469) on top of the structurally unsatisfiable
   99-case gate. The sentinel string in the synthetic `d` field
   (`OUTCOME_SENTINEL_MUST_NOT_BE_PARSED`, run.py:408) is a genuinely good
   self-test: any future regression that parses `d` crashes the smoke.

## Contract fidelity — verified correct

- **Primary metric.** Condition number of the four-column design after unit-L2
  scaling of non-intercept columns only (run.py:278-288), exactly the contract's
  diagnostic-scaling rule; centering once at the pooled 198-row mean with no other
  transform (292-296).
- **Secondary metrics all present** (run.py:300-363): rank and singular values;
  per-band min/max/median/IQR/distinct/n; per-row hat leverage (pinv-based, scale-
  invariant), max leverage, top-10 distinct patients; full leave-one-patient-out
  sweep recomputing the same centering and scaling per deletion.
- **All nine `positive_rule` clauses** map one-to-one onto the `gates` dict
  (run.py:340-350) with thresholds matching the frozen constants.
- **Outcome blindness holds.** `load_keys_without_outcomes` (run.py:203-234) verifies
  the exact five-column header (the contract's permitted `d`-existence check), then
  extracts only the first two fields by comma position; the remainder is never
  sliced, split, parsed, or retained. Delimiter counting scans the line but parses
  nothing. Whole-file SHA-256 hashing is the contract's own input-identity
  requirement, not column access. No other code path touches the file. The harness
  verified this independently.
- **Caps respected.** One variant, one seed (0, unused beyond declaration since the
  probe is deterministic), zero GPU, no bootstrap, no network. Stopping rule honored:
  nothing downstream of the design audit exists in the code.
- **Claim discipline.** Summary status uses only `POSITIVE_PATTERN` /
  `NEGATIVE_PATTERN` / `SMOKE_ONLY`; the printed interpretations (run.py:511-518)
  track the contract's `positive_pattern` / `negative_pattern` language, including
  the "computationally estimable only" scope and the "not evidence against tissue
  composition or the parent association" clause. No stronger sentence appears.
- **Approval gate.** Marker blob checked against the live contract blob (both
  `e7071541…`), plus a literal-drift guard on the frozen thresholds
  (run.py:133-140). Correct refusal semantics; smoke exempt but gate-incapable.
- **Required outputs.** All seven contract-listed artifacts are written
  (`per_row_design.csv` is this contract's per-sample table), plus the split and
  determinism manifests and `exclusions.csv`.

## Non-blocking findings

1. **Degenerate-geometry path emits non-strict JSON.** A zero column norm or zero
  trailing singular value returns `inf` (run.py:283, 287), which `json.dumps` writes
  as bare `Infinity` in `design_diagnostics.json` / `summary.json` — invalid strict
  JSON — and the `singular_values` list is empty in the norm-zero branch despite the
  contract's "all four singular values." Gates fail in every such case, so no wrong
  positive is possible; consider serializing `null` or failing `EXIT_DESIGN` instead.
2. **Empty-band taxonomy.** A primary band present in per_patient but absent from the
  audit surfaces as an `AssertionError` → exit 12 "harness fault" (run.py:180)
  rather than a classified input/join failure. Fail-loud, wrong label only.
3. **`run_log.txt` is best-effort.** It is written only on the success path
  (run.py:507) and omits the final summary/interpretation prints (509-518); on any
  failure the console is the sole record. The 004-era traceback-to-stderr lesson is
  honored (run.py:530-532), so this is acceptable, but a partial log write in the
  failure handler would improve forensics.
4. **`reserved_cases_accessed: 0` and `outcome_values_read: 0` are by-construction
  constants** (run.py:196, 379, 478-479), not measurements. They are honest given the
  code, but B1 shows the first can be asserted while a reserved case sits in the
  split manifest; after the B1 fix they become defensible.
5. **`numpy==2.5.2` pin unverified by the record.** The harness smoke passed, implying
  an importable numpy, but `verification.json` does not state the installed version.
  A wrong pin fails loudly at `pip install`, so risk is bounded. The real run's
  `environment.txt` will settle it.
6. Readability is good: the module docstring states the experiment, its stopping
  behavior, and the meaning of both patterns; phases are narrated; thresholds carry
  contract provenance comments; progress prints are present and the plain-English
  close is faithful. No opacity finding.

## Verdict

Two blocking findings, both narrow and mechanically fixable without touching the
estimand, thresholds, outputs, or scope: make the join gate bidirectional (B1) and
account for filtered rows (B2). Everything else — outcome blindness, the frozen
metric chain, gate mapping, determinism, smoke — implements the approved plan
faithfully.

```json
{"verdict": "REVISE", "blocking": ["B1 (rules 1-2): join gate enforced outcome->audit only; unmatched audit-side or reserved cases are silently ignored yet written into split_manifest.csv, and the run.py:271-273 set-equality check is vacuous by construction — add audit_keys != outcome_keys refusal (EXIT_JOIN) in build_design", "B2 (standards item 2): 198 band-1 audit rows and 99 band-1 per_patient keys are dropped with no exclusions.csv line and no total anywhere in the bundle; summary will claim exclusion_rows: 0 — record the band-filter drops with reasons and file-total row counts"], "note": "Faithful implementation of the approved outcome-blind design audit; blocked only on one-directional join validation and unaccounted filtered rows, both minimal EXIT_JOIN/logging fixes."}
```
