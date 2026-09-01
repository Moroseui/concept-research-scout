# Probe code review — idea 046, round 2

Artifact under review: `probes/046/run.py` + `probes/046/requirements.txt`
(commit "idea 046: probe code (round 2)"), judged against
`ideas/046/probe_contract.yaml` (git blob
`3996009bccfcfa939984fed051ee303a29a960a0`) and `ideas/046/feasibility.md`.
The round-1 review (preserved in git at commit 8637cab) returned REVISE with
two blocking findings, B1 and B2, and the explicit instruction that scope
must not expand while fixing them.

Review method: static, line-by-line, plus a full diff of round 1 → round 2
(`git diff 12f22db 3b989a4 -- probes/046/`). This review environment cannot
execute Python; `probes/046/verification.json` attests the round-2 smoke
completed under 60 seconds with matching determinism manifests, status
`SMOKE_ONLY`, and two new attestations (`smoke_residual_values_persisted`,
`smoke_ordering_verdict_is_computed`), each verified statically against the
code below. Independently re-verified in this round: the contract blob above
equals both the pin in `ideas/046/HUMAN_APPROVED_PROBE` and the current
`probe_contract.yaml` bytes; the frozen input's SHA-256 (`1d01551c...`)
matches `run.py:47` and the contract pin; the input remains 298 lines
(header + 297 rows). `ideas/046/contract_requirements.md` does not exist, so
review criterion 5 (requirements conformance) remains not applicable.

## Diff containment

The round-2 change to claim-bearing code is confined to `run.py` (28 lines:
`measure()` and `summarize_definitions()` signatures and bodies, plus the
two call sites in `run()`) and the two new `verification.json` attestations.
No gate, cap, cohort rule, exposure rule, output set, or status classifier
changed. The scope-containment instruction was respected — including by
*not* adopting the optional round-1 suggestions, which were non-blocking.

## Resolution of round-1 blocking findings

### B1 — RESOLVED: both residuals computed and persisted as numeric values

`measure()` now computes `stable_residual` via `math.fsum` and
`ordinary_residual` via naive built-in `sum` over the same contributions
(`run.py:256-257`), asserts both finite (`run.py:258-259`), and
`summarize_definitions()` records both numeric values in the audit dict
(`run.py:292-293`), which is written verbatim to `definition_audit.json`
(`run.py:373`). The primary metric's *value* — the contract's "absolute
algebraic residual" — is now `stable_summation_residual` in a required
output, and the ordinary-summation residual is labeled
`ordinary_summation_residual_diagnostic_only` and plays no pass/fail role
anywhere: the tolerance gate consumes only the stable residual
(`run.py:294`, `run.py:346-347`), exactly as `analysis.tolerance` directs.

Exposure check, repeated for the two new persisted numbers: both are
rounding-scale magnitudes (relative error of summation, ~1e-16 of the gap
scale) and appear on none of the `no_result_exposure` prohibitions
(case_id, d/delta/c values, ranks, shares, curve coordinates, band means,
band-gap). Round 1 pre-cleared recording them; confirmed safe as
implemented.

Interpretive note, recorded for the census-contract author rather than as a
defect: both residuals share the fsum-based `direct_gap` reconstruction
(`run.py:254-255`) and differ only in how the contribution decomposition is
summed. That is a defensible reading of the tolerance clause — it isolates
the summation-routine effect on the decomposition side, which is what the
diagnostic is for — and the contract does not specify otherwise.

### B2 — RESOLVED: both frozen orderings constructed; verdict measured, not asserted into existence

`summarize_definitions()` now builds both contract-frozen order-key lists —
`sorted((-delta, case_id))` for descending signed and
`sorted((-abs(delta), case_id))` for descending absolute
(`run.py:282-283`), matching `preprocessing.ordering` exactly (ascending
sort on the negated primary key yields descending order with `case_id`
ascending as tiebreak). Uniqueness is measured per ordering
(`run.py:284-285`), the verdict derived (`run.py:286`), asserted
(`run.py:290`), and emitted as the computed boolean
`deterministic_secondary_case_id_rule_defined` (`run.py:298`) — the
hardcoded `True` is gone. This is precisely the fix shape round 1
specified.

Pairing correctness verified: `measure()` builds `deltas` iterating
`sorted(cases)` (`run.py:242-247`) and returns `sorted(cases)` as
`case_ids` (`run.py:260`), so `zip(case_ids, deltas)` at `run.py:282-283`
pairs each case with its own delta. Both lists live and die in memory; no
identifier or rank reaches any artifact or log, per the in-code comment at
`run.py:280-281`.

## Non-blocking findings (round 2)

1. **`assert deterministic_ordering` routes a hypothetical False to exit
   12, not the negative pattern.** A tie the case_id rule failed to resolve
   would arguably be the negative pattern's "stated rule is incomplete"
   (→ `DEFINITION_REVISION_REQUIRED`), but the assert at `run.py:290` would
   surface it as an unexpected fault instead. Unreachable in practice: the
   cohort gate (`run.py:199-200`) guarantees unique case IDs, so every
   `(-delta, case_id)` tuple is distinct regardless of delta values. The
   behavior is fail-loud, never fail-silent, and matches the fix round 1
   sanctioned; a `FEASIBLE_DEFINITION_AUDIT` status can only ever be
   emitted with the verdict measured True. Recorded, not blocking.
2. **Round-1 non-blocking findings 1-8 stand as recorded.** In particular:
   the `human_approved: false` marker-convention reading (round-1 finding
   1) remains on the record ahead of any run; `target_share_definable`
   still keys every target to the global `summaries_defined` conjunction
   (`run.py:300`) rather than per-summary booleans; the empty-input path
   still exits 12; `run_log.txt` still omits the two manifest JSON lines;
   the `rounded_signed`/`rounded_absolute` naming nit stands (they are hex
   encodings, and `float.hex()` still distinguishes `-0.0` from `0.0` in
   the tie *counts* — inconsequential, zero counts are reported
   separately); smoke still cannot exercise the all-defined branch (8
   synthetic cases leave `k = 20` undefinable). None of these blocks, and
   leaving the optional ones unadopted was the correct application of the
   no-scope-expansion instruction. They may be revisited, if ever, in the
   separate census contract.

## Standards checklist (each verified against round-2 code)

1. **Determinism manifests: MET.** Start (`run.py:328-329`) and end
   (`run.py:386-390`) manifests written and printed, compared for exact
   equality with a named failure on divergence (`run.py:387-388`).
2. **Exclusions log: MET.** Every dropped row logged with a reason
   (`run.py:193`, `run.py:335`); totals in `summary.json` (`run.py:376`).
3. **Assertion per transform: MET.** Load (`run.py:196, 208-209`), split
   freeze (`run.py:232-233`), measurement (`run.py:239, 246, 251,
   258-259`), summarization (`run.py:275, 289-290`), manifest
   (`run.py:171`).
4. **Declared state: MET.** Seed and paths are top-level constants or CLI
   arguments (`run.py:40-53, 108-113`); no network; the `--input-csv`
   override remains neutralized in real mode by the SHA-256 gate
   (`run.py:326-327`). Determinism note: `direct_gap` iterates a set, but
   `math.fsum` is order-independent, and the ordinary residual sums a
   deterministically ordered list — outputs are hash-stable across runs.
5. **Split-before-outcome: MET.** `split_manifest.csv` written and hashed
   (`run.py:324`, `run.py:213-229`) before the input CSV is first opened
   (`run.py:325`).
6. **Harness smoke: MET** (statically; runtime attested by
   `verification.json`). Synthetic input, authority sentinel that is not a
   blob (`run.py:117-118`), forced `SMOKE_ONLY` (`run.py:352-353`) which
   satisfies neither contractual pattern.

## Contract-fidelity confirmations (unchanged from round 1, spot-re-verified)

- Primary metric formula, stable summation, and 1e-12 tolerance match the
  contract (`run.py:253-257, 346-347`); algebra failure exits 5 and is
  never reframed as the negative pattern.
- Cohort gate implements the full `row_gate`; caps respected (one variant,
  zero GPU, one unused seed, single pass, 5-minute wall check at
  `run.py:358-359`); required outputs all written (`run.py:370-384, 401`).
- No-result-exposure discipline holds across every output, log line, and
  failure message, including the two newly persisted residuals.
- Claim discipline: the three status strings are exactly the contract's
  two patterns plus `SMOKE_ONLY`; the plain-language templates
  (`run.py:392-399`) claim drafting authorization only.

## Verdict

Both round-1 blocking findings are resolved exactly as specified, the fix
diff contains nothing else, and every identity anchor (contract blob,
approval marker, frozen input hash) re-verifies. The audit now records what
it measures and measures what it certifies.

```json
{"verdict": "APPROVE", "blocking": [], "note": "B1 and B2 resolved as directed with no scope expansion: both residual values persisted in definition_audit.json (ordinary labeled diagnostic-only, no gate role) and both frozen orderings constructed with the tie-rule verdict measured rather than hardcoded."}
```
