# Probe code review — idea 046, census probe (contract v2), round 2

Artifact under review: `probes/046/run.py` + `probes/046/requirements.txt`
(commit "idea 046: probe code (round 2)", e1c710b), judged against
`ideas/046/probe_contract.yaml` at git blob
`942e530737c90b666baa4c9985fd0329296ef140` and `ideas/046/feasibility.md`.
Round 1 (preserved in git at f3fb2df) returned REVISE on exactly one
blocking finding, B1: the contract's v1 lineage-guard comparison —
required by `analysis.secondary_metrics` (last item), frozen in
`baselines[0]`, and named as a lineage invalidating failure — was absent
from `run.py`. This round verifies the revision.

Review method: static, line-by-line, plus a full diff of round 1 → round 2
(`git diff eea79cb e1c710b -- probes/046/`). This review environment
cannot execute Python; `probes/046/verification.json` attests the harness
smoke was re-run after the revision (checked 2026-09-01T18:47:34-04:00 =
22:47:34Z, after the round-1 review) and passed: status `SMOKE_ONLY`, 24
synthetic cases, 14 required outputs, under 60 seconds, two-run byte
determinism across all seven scientific outputs, `real_census_executed:
false`. Independently re-verified in this round: the contract blob above
was recomputed from the on-disk contract bytes and equals the pin in
`ideas/046/HUMAN_APPROVED_PROBE` (approved 2026-09-01T22:37:49Z); the
frozen input `probes/023/results/results_v2/per_patient.csv` hashes to
the contract-pinned `1d01551c…` (298 lines = header + 297 rows); the v1
bundle `probes/046/results/results_v2/` is untouched in the working tree;
`ideas/046/contract_requirements.md` does not exist, so review criterion 5
is not applicable.

## Resolution of round-1 blocking finding B1 — VERIFIED CLOSED

The revision implements the comparison with exactly the binding effects
round 1 specified, choosing the in-code-constants option:

1. **Frozen values with provenance.** `run.py:51-55` transcribes the v1
   guard values as annotated constants ("Frozen lineage guards from
   contract v2 baselines[0], produced by the completed v1 definition
   audit"): residual `6.938893903907228e-18`, sign counts 54/6/39, tie
   counts 5/5. Verified this round to be transcription-exact against BOTH
   sources: the contract's `baselines[0]` text and the actual v1 artifact
   `probes/046/results/results_v2/definition_audit.json`
   (`stable_summation_residual`, `sign_counts`, `tie_counts`).
2. **Real mode only, after the guards are recomputed.**
   `compare_v1_lineage_guards` (`run.py:357-401`) is called at
   `run.py:452`, immediately after `summarize_census` returns and before
   any status exists. The comparison covers the full `baselines[0]` value
   set: paired cases (99), additive-identity residual (exact float
   equality — correct for a determinism guard), denominator definedness,
   ordering determinism (case_id uniqueness, the same criterion that
   makes the frozen tie rule total), sign counts, and tie counts.
   Top-k/target definability, the remaining `baselines[0]` clause, is
   entailed rather than compared: the cohort gate pins n = 99 = v1's
   count before this point, and the three denominator gates
   (`run.py:274-275, 292-293, 309-310`) plus the always-terminating
   positive-mass curve (`run.py:318`) make every frozen summary defined
   whenever execution reaches the comparison. No gap.
3. **Loud, named failure before any status.** Disagreement routes to
   `fail(EXIT_OUTPUT, "v1 lineage guard disagreement: observed=…
   expected=…")` (`run.py:393-394`), dumping both dicts. This fires
   before the status assignment (`run.py:454`) and before the first
   results artifact is written (`resolved_config.json`, `run.py:467`);
   the run exits nonzero with no `summary.json`, so `CENSUS_COMPLETE` is
   unreachable on a lineage disagreement — the silent-failure surface B1
   named is closed.
4. **Verdict recorded in census_summary.json.** The full comparison
   record (status, `compared`, tie-count space, observed, expected) is
   attached at `run.py:453` and persisted via the `census_summary.json`
   write at `run.py:484`.
5. **Smoke skips visibly.** In smoke the function returns
   `{"status": "SKIPPED_SMOKE_SYNTHETIC_DATA", "compared": false, …}`
   (`run.py:359-364`), which lands in the smoke bundle's
   `census_summary.json` — inside the byte-determinism compared set —
   and is attested in `verification.json`
   (`smoke_v1_lineage_comparison`). Smoke performs no comparison against
   synthetic data, exactly as required.
6. **The tie-count space is resolved as round 1 demanded.** Round 1
   required either comparing in v1's space or naming the difference. The
   revision does the stronger thing: ties are re-counted in **delta**
   space, before division by 99 (`run.py:366-373`), with the comment
   naming why ("avoids assuming that floating-point division is
   injective"), and the space is declared in the persisted record
   (`tie_count_space: "delta_before_division_by_99"`) and in
   `verification.json` (`v1_tie_comparison_space`).

**Spurious-fire risk checked and excluded.** Because the guard demands
bit-for-bit residual equality, this round verified against the executed
v1 code (git `3b989a4`, `run.py` lines 240-257) that v2's `measure()`
reproduces v1's computation exactly: same per-case
`delta = band3 − band2`, same `delta / n`, same
`direct_gap = fsum(d₃)/n − fsum(d₂)/n`, same
`abs(fsum(contributions) − direct_gap)` under `math.fsum` — and `fsum`
is order-independent (correctly rounded exact sum), so iteration-order
differences between the two implementations cannot move the value. The
recomputed residual on the pinned input is therefore bit-identical to
the frozen constant by construction.

## Non-blocking findings

1. **Tie-counting mechanism differs from v1's, immaterially, on this
   input.** v1 counted ties via `.hex()` encodings (git `3b989a4`,
   lines 276-279); the guard uses float-equality `set()` membership
   (`run.py:371-372`). For finite doubles these diverge only at signed
   zero (`+0.0 == -0.0` but different hex encodings; nonfinite values
   cannot reach this point past the cohort gate). v1's own recorded
   output — six zero deltas with signed tie count 5 — is consistent only
   with all six zeros sharing the `+0.0` representation, so the two
   mechanisms provably agree on this exact frozen input; any divergence
   on a different input fires the guard loudly, which is the fail-safe
   direction. Recorded for the interpreter; no change required.
2. **Sign counts are compared across spaces, immaterially.** The guard's
   observed `sign_counts` come from contribution space (`run.py:341-343`)
   while v1 counted in delta space. Division by 99 preserves sign and
   zeroness except for sub-denormal underflow (requires
   |delta| < ~2.4e-321), impossible for values parsed from this CSV's
   decimal magnitudes; the one summary where division is genuinely
   non-injective — tie counts — is correctly redone in delta space. Any
   surprise fires loudly.
3. **Exit-code taxonomy nit.** A lineage disagreement exits via
   `EXIT_OUTPUT` (7, docstring: "output/determinism") rather than a
   dedicated lineage code; `EXIT_DEFINITION` (6) remains defined but
   unreachable and the docstring still labels 6 "scope" (round-1 finding
   4 carries forward). The failure message names the lineage class and
   `verification.json` documents `real_run_lineage_disagreement_exit: 7`,
   so diagnosability is preserved.
4. **Carried forward unchanged from round 1** (all previously judged
   non-blocking; none blocks now): redundant audit fields (`delta`,
   `d_band2`, `d_band3` in `per_case_contributions.csv`) still carry no
   explicit redundant/audit label; an empty-but-headered CSV hits the
   `run.py:205` assert (exit 12) before the cohort gate can name it;
   `split_manifest.json` is written twice (`run.py:236-238`, hashed
   version persists, both precede input open); single wall-time
   checkpoint (`run.py:455-456`); `run_log.txt` omits the two
   determinism-manifest JSON stdout lines; 99 per-pair progress lines
   are noisy but compliant.
5. **Round-1 finding 1 is fixed.** The stale v1 comment at the exclusion
   branch now correctly states the v2 rule (`run.py:200-201`: analyzed
   IDs are emitted in the census table; excluded band-1 rows get
   source-line provenance).

## Scope check

The round-1 → round-2 diff touches exactly: the three frozen constants,
the comment fix, `compare_v1_lineage_guards`, its call site and the
`census_summary.json` field, and the refreshed `verification.json`
attestation. No new input is read (the constants option was chosen over
reading the v1 bundle at runtime), no output beyond the mandated
comparison record is added, no formula, ordering, gate, cap, or claim
changed. No scope expansion.

## Contract-fidelity confirmations (re-verified at round-2 line numbers)

- **Primary metric.** Complete ordered per-case signed contribution table
  with `signed_rank` (`run.py:470-476`) and signed cumulative sequence
  (`run.py:477-479`): `c_i = delta_i / len(cases)` with the cohort gate
  pinning n = 99 in real mode (`run.py:213-214, 256`), stable prefix
  sums via `math.fsum` (`run.py:276-284`), descending contribution with
  case_id-ascending tiebreak (`run.py:271`).
- **Secondary metrics.** Lorenz curve with explicit (0,0)/(1,1)
  endpoints and monotonicity assert (`run.py:294-303`); both top-k
  families over frozen k = 1, 5, 10, 20 (`run.py:320-330`);
  positive-mass 50%/80% crossings with achieved shares
  (`run.py:331-337`); sign and tie counts (`run.py:339-345`); and now
  the v1 lineage guards (`run.py:357-401`). The signed curve is never
  called a Lorenz curve; `signed_fraction_of_net` is unclamped, per the
  contract.
- **Identity and cohort gates.** Approval marker parsed, 40-hex blob
  compared to the recomputed contract blob with required implementation
  literals cross-checked (`run.py:124-143`); input SHA-256 gated against
  the frozen pin in real mode (`run.py:425-426`), neutralizing
  `--input-csv`; full row_gate — required columns, finite d, unique
  case-band keys, exactly-99 paired cases, identical band-2/3 case sets,
  no admitted row outside bands 2 and 3 (`run.py:183-219`).
- **Caps and stopping rule.** One variant, zero GPU, one declared-unused
  seed, single pass, immediate stop on any named failure via `fail()`;
  `resolved_config.json` records variants 1 / gpu_minutes 0
  (`run.py:458-463`). Wall cap enforced in-code (`run.py:455-456`).
- **Required outputs.** All 14 contract-listed artifacts written
  (`run.py:427, 434, 467-512`); `split_manifest.csv` and smoke-only
  `smoke_input.csv` are permitted extras; `summary.json` carries
  `idea_id`/`status`, omits `phase` (tolerated under S2b).
- **Claim discipline.** Status strings exactly `CENSUS_COMPLETE` /
  `SMOKE_ONLY`; no directional negative anywhere; the plain-language
  template (`run.py:505-510`) claims descriptive accounting only and
  disclaims stable carriers and population concentration. Naming cases
  in outputs is authorized by v2 `claim_discipline.permitted`.
- **Scope.** Reads exactly the frozen table and authority metadata; no
  phenotype, reserved-case, image, voxel, or cache access exists in the
  code; `reserved_cases_accessed: 0` recorded from the split record.
- **Authority convention.** The in-file `human_approved: false` line
  under a fresh marker binding the exact blob is the standing
  marker-file convention (recorded since the v1 round-1 review); it
  carries forward unchanged.

## Standards checklist (each item verified)

1. **Determinism manifests: MET.** Start manifest written and printed
   (`run.py:427-428`); end manifest recomputed from the same input,
   compared for exact equality with a named `EXIT_OUTPUT` failure on
   divergence, then written and printed (`run.py:499-503`).
2. **Exclusions log with reasons: MET.** Every non-admitted row logged
   with `source_line` and reason (`run.py:202, 434`); totals in
   `summary.json`.
3. **Assertion per transform: MET.** Load (`run.py:205, 217-218`), split
   freeze (`run.py:239-242`), measurement (`run.py:248, 254, 257, 260,
   264`), summaries (`run.py:272, 285-286, 300-303, 318, 346`), lineage
   guard (`run.py:393`, hard gate), manifest (`run.py:179`), split-vs-
   cohort cross-check (`run.py:435`).
4. **Declared state: MET.** Seed and paths are top-level annotated
   constants (`run.py:41-61`); seed set once, never consumed; no
   analysis-time network; stdlib only (`requirements.txt`). Two-run byte
   determinism of all scientific outputs re-attested post-revision in
   `verification.json`.
5. **Split manifest hashed before outcome access: MET.** `freeze_split`
   writes and SHA-256-hashes the anonymous manifest (`run.py:222-243`,
   called at `run.py:423`) strictly before `start_manifest` first opens
   the input CSV (`run.py:424`).
6. **Smoke: MET** (statically; runtime attested by the refreshed
   `verification.json`). Synthetic 24-case input exercising every frozen
   top-k, both share targets, and all sign branches; authority bypassed
   with a non-hex sentinel (`run.py:125-126`); status forced `SMOKE_ONLY`
   (`run.py:454`), satisfying no contractual pattern; the new lineage
   comparison is skipped in smoke with the skip visible in output.

## Practicalities

Unchanged from round 1: stdlib only, no pip installs, `--output-dir`
required with no interactive prompts, default input resolved relative to
the repo root, output directory required empty (compatible with the
driver's blob-scoped output-dir scheme). Sub-second CPU workload against
a 5-minute cap.

## Verdict

The single round-1 blocking finding is closed exactly as specified: the
v1 lineage guards are frozen in-code with provenance, compared in real
mode after recomputation, fail loudly with a named message before any
status can be written, are recorded in `census_summary.json`, skip
visibly in smoke, and resolve the delta-versus-contribution tie-space
ambiguity in v1's own space. The revision touches nothing else; the
spurious-fire risk of bit-exact comparison was checked against the
executed v1 code and excluded by construction. All remaining findings
are non-blocking nits already on the record.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Round-1 B1 closed exactly as specified — frozen v1 lineage guards compared in real mode, fail-loud pre-status, recorded in census_summary.json, smoke-skip visible, tie space resolved in delta space; no scope expansion; remaining findings non-blocking."}
```
