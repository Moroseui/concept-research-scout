# Probe code review — idea 046, round 1

Artifact under review: `probes/046/run.py` + `probes/046/requirements.txt`
(commit "idea 046: probe code (round 1)"), judged against
`ideas/046/probe_contract.yaml` (git blob
`3996009bccfcfa939984fed051ee303a29a960a0`, verified equal to the pin in
`ideas/046/HUMAN_APPROVED_PROBE`) and `ideas/046/feasibility.md`.

Review method: static, line-by-line. This review environment cannot execute
Python, so the smoke run was not re-executed here; `probes/046/verification.json`
attests smoke completed under 60 seconds with matching determinism manifests
and status `SMOKE_ONLY`, and every smoke property claimed there was verified
statically against the code. Independently re-verified in this review: the
contract blob and marker identity above; the frozen input's SHA-256
(`1d01551c...`, matching `run.py:47` and the contract pin); the input's
header/row structure (298 lines, strata 1/2/3). `ideas/046/contract_requirements.md`
does not exist, so review criterion 5 (requirements conformance) is not
applicable.

## Blocking findings

### B1 — The ordinary-summation residual diagnostic is never computed or recorded, and no residual value is persisted at all (contract fidelity, rule 1)

Contract `analysis.tolerance` states: "The primary residual must be <= 1e-12
using IEEE-754 double precision and a stable summation routine. **The
ordinary-summation residual is recorded only as a numerical diagnostic.**"

`measure()` (`run.py:253-257`) computes only the `math.fsum`-based residual.
The ordinary-summation (naive accumulation) residual is never computed and
appears in no output. Additionally, the primary residual's *value* is never
persisted anywhere: `definition_audit.json` carries only the boolean
`algebra_residual_within_tolerance` (`run.py:282`) and `summary.json` only
`primary_metric_pass` (`run.py:367`). The contract's primary metric — "Absolute
algebraic residual abs(sum_i(c_i) - (mean_i(d_i,band3) - mean_i(d_i,band2)))"
— therefore appears in no required output, only a predicate derived from it.

Recording both residuals is contract-sanctioned and exposure-safe: the
tolerance clause explicitly directs the ordinary-summation residual to be
recorded, and a rounding-scale residual is not on the `no_result_exposure`
prohibited list (case_id, d/delta/c values, ranks, shares, curve coordinates,
band means, band-gap). Fix: compute both residuals, record both numeric values
in `definition_audit.json` (stable-summation residual as the primary metric
value; ordinary-summation residual labeled diagnostic-only, no pass/fail
role).

### B2 — The frozen orderings are never constructed and the tie-rule audit result is hardcoded `True` (contract fidelity rule 1; silent-failure surface rule 2)

Contract `preprocessing.ordering` defines two orderings "for audit purposes
only" (descending signed by `delta_i` then `case_id` ascending; descending
absolute by `abs(delta_i)` then `case_id` ascending), and
`analysis.secondary_metrics` item 3 requires tie counts "**confirming** that
the frozen secondary case_id rule makes every ordering unique." The
`positive_pattern` certifies "deterministic ordering resolves every tie."

`run.py` emits the tie counts (`run.py:276-277`) but never constructs either
ordering; the confirmation is the constant
`"deterministic_secondary_case_id_rule_defined": True` (`run.py:286`) — an
audit output that cannot be false on any input. The property is in fact
entailed by the duplicate-key cohort gate (`run.py:199-200`), but this
repository's standing rule (decision ledger, 2026-08-18) is that claim-bearing
code is verified against artifacts, not asserted; a definition audit whose one
job is to verify the frozen definitions on the real table may not hardcode one
of the verdicts the positive pattern certifies. Fix (three lines, in memory
only, nothing emitted): build both sort-key lists
`(-delta_i, case_id)` and `(-abs(delta_i), case_id)`, assert each key set has
no duplicates, and derive the boolean from that check.

## Non-blocking findings

1. **`human_approved: false` self-tension in the approved contract.** The
   contract's first invalidating failure names execution "while
   human_approved remains false," yet the approved bytes themselves end with
   `human_approved: false` — read literally, every execution is invalidating.
   Repository precedent resolves this: `ideas/004/probe_contract.yaml:299` and
   `ideas/023/probe_contract.yaml:142` both carry `human_approved: false`
   under the marker-based convention, where the `HUMAN_APPROVED_PROBE` marker
   binding the exact contract blob *is* the fresh approval (flipping the field
   would change the blob and stale the marker by construction).
   `verify_authority()` (`run.py:116-135`) implements the marker gate
   correctly and strictly. Recorded here, before any run, so the
   interpretation is on the record rather than litigated after; the future
   census contract should word this clause as marker-bound.
2. **Per-summary definability is misattributed.** `target_share_definable`
   maps every target to the *global* conjunction `summaries_defined`
   (`run.py:278-279, 288`) rather than to that summary's own condition
   (positive-mass nonzero), and the contract's enumerated summaries (signed
   cumulative curve, Lorenz coordinates) have no individually named booleans —
   definability must be inferred from the `denominators` block. On the real
   table all flags will agree, and the denominator booleans do identify any
   culprit, so this does not block; but since B1 already reopens
   `definition_audit.json`, keying one boolean per contract-enumerated summary
   would make the negative pattern's "a named summary is undefined" literal.
3. **Empty-input path exits 12, not a named failure.** A header-only CSV
   trips `assert len(selected) + len(excluded) > 0` (`run.py:196`),
   surfacing as AssertionError → exit 12 (unexpected fault) instead of a
   named input/cohort failure. Unreachable in real mode behind the SHA-256
   gate; tidy-up only.
4. **`run_log.txt` omits the two manifest JSON lines.** The determinism
   manifests are printed via bare `print` (`run.py:317, 378`), not `emit`, so
   the persisted log diverges slightly from the console. Harmless; the
   manifests are persisted as their own required-adjacent JSON files.
5. **`exclusions.csv` records `source_line` only, by design.** The in-code
   comment (`run.py:192`) correctly notes the contract forbids persisting
   case identifiers. Since every case contributes exactly its stratum-1 row
   to the exclusions, line numbers convey no selection information. Accepted;
   reasoning recorded.
6. **Naming nit.** `rounded_signed`/`rounded_absolute` (`run.py:274-275`) are
   hex encodings, not roundings (good — the contract forbids rounding);
   rename. Also `float.hex()` distinguishes `-0.0` from `0.0`, so two zero
   deltas of opposite sign would not count as a hex tie despite numerical
   equality; zero counts are reported separately and the effect is
   inconsequential here, but worth a comment.
7. **Wall-time check runs once, post-measurement** (`run.py:346`). Fine for a
   seconds-long run; a genuine hang would never reach it. Acceptable since
   the 5-minute cap is a validity bound, not a watchdog.
8. **Smoke never exercises the all-defined branch.** With 8 synthetic cases,
   `k = 20` is undefinable, so smoke always computes
   `all_summaries_defined: false` (then forces `SMOKE_ONLY` regardless).
   Using ≥ 20 synthetic cases would let smoke exercise both classifier
   branches. Optional.

## Standards checklist (Hard code standards, each verified)

1. **Determinism manifests: MET.** Printed and written at start
   (`run.py:316-317`) and end (`run.py:377-378`), with input path, content
   hash, row/case counts, and seed; compared for exact agreement
   (`run.py:375-376`) with a named failure on divergence.
2. **Exclusions log: MET.** Every dropped row emits one line with a reason
   to `exclusions.csv` (`run.py:193, 323`); totals appear in `summary.json`
   (`excluded_rows`, `run.py:364`).
3. **Assertion per transform: MET.** Load (`run.py:196, 208-209`), split
   freeze (`run.py:232-233`), measurement (`run.py:239, 246, 251, 257`),
   summarization (`run.py:273, 280`), manifest (`run.py:171`).
4. **Declared state: MET.** Seed and paths are top-level constants or CLI
   arguments (`run.py:40-53, 108-113`); no network calls; no hidden
   mid-function state. The `--input-csv` override is rendered harmless in
   real mode by the SHA-256 gate (`run.py:314-315`).
5. **Split-before-outcome: MET.** `split_manifest.csv` is written and hashed
   (`run.py:213-229`) before the input CSV is first opened
   (`run.py:312` precedes `run.py:313`).
6. **Harness smoke: MET** (statically; runtime attested by
   `verification.json`). Accepts `--output-dir`, synthesizes its own input,
   bypasses no real gate (authority returns a non-blob sentinel,
   `run.py:117-118`), and is forced to `SMOKE_ONLY` (`run.py:340-341`), which
   satisfies neither contractual pattern.

## Contract-fidelity confirmations (what passes)

- Primary metric formula matches the contract exactly:
  `abs(fsum(c_i) - (mean_3 - mean_2))` with `c_i = (d_3 - d_2)/99`, stable
  summation via `math.fsum`, tolerance `1e-12` (`run.py:253-257, 334-335`) —
  the *comparison* is correct; only its recording is deficient (B1).
- Cohort gate implements the full `row_gate`: SHA-256 identity, required
  columns, finiteness, duplicate keys, 99 cases per band, identical band
  sets, non-primary strata excluded not admitted (`run.py:175-210, 314-315`).
- Authority gate: marker must bind the exact current contract blob
  (`run.py:121-127`), plus a literal-presence check on the approved text
  (`run.py:128-134`).
- Caps and stopping rule: one variant, zero GPU, one (unused) seed, fail-fast
  on first invalidating failure, single pass (`run.py` has no loop over
  variants or seeds); algebra failure exits 5 and is never reframed as the
  negative pattern (`run.py:334-335`), matching the contract's invalidating
  classification.
- No-result-exposure discipline holds across every output and log: all
  persisted/printed content is booleans, counts, hashes, paths, and
  anonymized indices; no case_id, d/delta/c value, rank, share, coordinate,
  mean, or gap is emitted (verified for `determinism_manifest_*.json`,
  `split_manifest.*`, `exclusions.csv`, `sample_audit.csv`,
  `definition_audit.json`, `summary.json`, `resolved_config.json`,
  `input_manifest.csv`, `run_log.txt`, stdout, and failure messages).
- Claim discipline: the three status strings are exactly the contract's two
  patterns plus `SMOKE_ONLY`; the plain-language templates
  (`run.py:380-387`) claim drafting authorization only, never dominance or
  concentration.
- Readability: module docstring with exit-code map, narrated phases,
  provenance-annotated constants, progress printing, plain-English closing
  template — the human can run and read this.
- Practicalities: stdlib-only (`requirements.txt` matches
  `environment_record`), no pip installs, no prompts, `--output-dir`
  external, Colab-compatible.

## Verdict

Both blocking findings are confined to the audit's recording/verification
layer; neither touches the estimator, the gates, the cohort, or the exposure
discipline, and both are small, contract-directed fixes. Scope must not
expand while fixing them.

```json
{"verdict": "REVISE", "blocking": ["B1: ordinary-summation residual diagnostic required by analysis.tolerance is never computed or recorded, and neither residual value is persisted — the primary metric appears in no output, only a boolean (rule 1, contract fidelity)", "B2: the two frozen orderings from preprocessing.ordering are never constructed; the tie-rule uniqueness verdict certified by the positive pattern is hardcoded True rather than measured (rules 1-2, contract fidelity / silent-failure surface)"], "note": "Faithful gate, cohort, and exposure implementation; REVISE only to record both residual values and to actually construct-and-assert the frozen orderings instead of hardcoding the audit verdict."}
```
