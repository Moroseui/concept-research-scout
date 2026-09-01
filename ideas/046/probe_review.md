# Probe code review — idea 046, census probe (contract v2), round 1

Artifact under review: `probes/046/run.py` + `probes/046/requirements.txt`
(commit "idea 046: probe code (round 1)", eea79cb), judged against
`ideas/046/probe_contract.yaml` at git blob
`942e530737c90b666baa4c9985fd0329296ef140` and `ideas/046/feasibility.md`.
This is round 1 for the v2 census contract; the reviews of the completed v1
definition-audit probe are preserved in git and are lineage context only.

Review method: static, line-by-line. This review environment cannot execute
Python; `probes/046/verification.json` attests the harness smoke completed
under 60 seconds with status `SMOKE_ONLY`, 24 synthetic cases, 14 required
outputs, and two-run byte determinism across all seven scientific outputs
(`real_census_executed: false`). Independently re-verified in this round:
the contract blob above was recomputed from the on-disk contract bytes and
equals both the pin in `ideas/046/HUMAN_APPROVED_PROBE` (approved
2026-09-01T22:37:49Z) and `run.py`'s own literal checks; the frozen input
`probes/023/results/results_v2/per_patient.csv` hashes to the contract-pinned
`1d01551c…` (298 lines = header + 297 rows) and is untouched in the working
tree, as is the v1 bundle. `ideas/046/contract_requirements.md` does not
exist, so review criterion 5 (requirements conformance) is not applicable.

## BLOCKING findings

### B1 — The contract's v1 lineage-guard comparison is not implemented

Three places in the approved contract bind the run to the completed v1
definition audit:

- `analysis.secondary_metrics`, last item: residual, denominator checks,
  cohort counts, and deterministic-order checks are to be "repeated as
  execution guards **and compared with the completed v1 audit**";
- `baselines[0]` freezes the comparison values: additive residual
  6.938893903907228e-18, all denominators and summaries defined, 99 paired
  cases, deterministic orderings, sign counts 54 positive / 6 zero / 39
  negative — "lineage guards, not scientific comparators";
- `invalidating_failures`, lineage clause: "the repeated v1 guard values
  disagree without a named implementation explanation" is an invalidating
  failure, and the stopping rule requires an immediate stop on any
  invalidating failure.

`run.py` repeats the guards (residual at `run.py:256` gated at
`run.py:390-391`; denominators at `run.py:267-268, 285-286, 302-303`;
cohort counts at `run.py:199-210`; ordering uniqueness at `run.py:265`;
sign/tie counts at `run.py:332-338`) but **never compares any of them with
the v1 audit**. Grep confirms: no read of the authority-listed prior bundle
(`probes/046/results/results_v2/definition_audit.json`), no frozen v1
constants (the residual literal, 54/6/39) anywhere in the file. The only
occurrence of `results_v2` is the idea-023 input path at `run.py:55`.

Consequence (rules 1 and 2): if a v2 run's recomputed guards diverged from
the v1 audit — a parsing difference, an environment change, a subtly
different summation path — the run would emit `CENSUS_COMPLETE` and the
lineage invalidating-failure class would be structurally undetectable at
the only point the stopping rule can act on it. That is precisely the
silent-failure surface this review exists to catch: the probe prints a
success status on an input/pipeline state the contract defines as invalid.

Fix shape (not prescriptive on mechanism, binding on effect): in real mode
only, after the guards are recomputed, compare them against the frozen v1
values — sourced either as in-code constants transcribed from the
contract's `baselines[0]` block (with provenance comments) or from the
authority-listed v1 `definition_audit.json` — and route any disagreement to
a named lineage failure exit before any status is written; record the
comparison verdict in `census_summary.json`. Smoke must skip the comparison
(synthetic data) and the skip must be visible in the output. One
specification the revision must make explicit: v1 counted exact ties in
**delta** space (5/5, via hex encodings) while `run.py:337-338` counts them
in **contribution** space (post-division); division by 99 preserves sign at
these magnitudes but is not injective over doubles in principle, so the
revision must either compare in the same space as v1 or name the space
difference as the contract's "named implementation explanation" in the
comparison record.

## Non-blocking findings

1. **Stale v1 comment misstates the governing contract.** `run.py:194`:
   "Contract forbids persisting case identifiers; source line is sufficient
   audit provenance." False under v2 — this contract *mandates* naming the
   99 analyzed cases in the outputs; only the v1 audit forbade exposure.
   The behavior (exclusions keyed by `source_line` + reason) still
   satisfies the exclusions requirement, since the excluded rows are band-1
   rows and no analyzed case is omitted from the per-case outputs, but the
   comment is a v1 carryover asserting a rule that no longer exists and
   should not survive to a future reader. Fix opportunistically at B1
   revision time.
2. **Redundant audit fields are unlabeled.** The contract permits `delta_i`
   "only as an explicitly redundant audit field"; `run.py:414-420` emits
   `delta`, `d_band2`, and `d_band3` with no in-file marking of their
   redundant/audit status (all three are verbatim or arithmetic restatements
   of frozen inputs, so the behavior is contract-compatible). A one-line
   label in the docstring or `census_summary.json` closes the gap.
3. **Empty-but-headered CSV exits 12, not a named class.** `run.py:198`'s
   assert fires before the cohort-count gate can name the failure. Fail-loud
   in the correct direction; same recorded nit as v1.
4. **`EXIT_DEFINITION` (`run.py:61`) is defined but unreachable**, and the
   docstring labels exit 6 "scope" while the constant says definition. No
   code path emits either meaning. Dead code / labeling mismatch.
5. **`split_manifest.json` is written twice** (`run.py:229-231`), the second
   write adding the CSV hash. Harmless; the hashed version is what persists,
   and both writes precede the input open.
6. **Single wall-time checkpoint.** `run.py:399-400` checks the 5-minute cap
   once, post-measurement and pre-output. Adequate for a deterministic
   sub-second run — a hang would produce no status at all — but it is a
   checkpoint, not continuous enforcement. Same pattern v1 ran under.
7. **`run_log.txt` omits the two determinism-manifest JSON lines** that go
   to stdout (`run.py:374, 447`); the driver console captures them. Same
   nit as v1.
8. **99 per-pair progress lines** (`run.py:388-389`) are noisy but satisfy
   the progress-printing standard and contain no unauthorized content.

## Contract-fidelity confirmations (verified line by line)

- **Primary metric.** The complete ordered per-case signed contribution
  table (`per_case_contributions.csv`, all 99 cases with `signed_rank`) and
  the signed cumulative sequence (`signed_cumulative_curve.csv`) are
  computed exactly as frozen: `c_i = delta_i / len(cases)` with the cohort
  gate pinning `len(cases)` to 99 in real mode (`run.py:249, 206-207`),
  stable prefix sums via `math.fsum` (`run.py:271-277`), descending
  contribution with `case_id` ascending tiebreak (`run.py:264`).
- **Secondary metrics.** Absolute-contribution Lorenz curve with explicit
  (0,0) and (1,1) endpoints, ascending-|c| ordering, and a monotonicity
  assert (`run.py:283-296`); both top-k families over the frozen
  k = 1, 5, 10, 20 (`run.py:313-323`); positive-mass 50%/80% smallest-k
  crossings with achieved shares (`run.py:324-330`); sign and tie counts
  (`run.py:332-338`). The signed curve is never called a Lorenz curve; the
  `signed_fraction_of_net` is not clamped to [0,1], per the contract.
- **Identity and cohort gates.** Approval marker parsed and its 40-hex blob
  compared to the recomputed contract blob (`run.py:118-137`, with required
  implementation literals cross-checked); input SHA-256 gated against the
  frozen pin in real mode (`run.py:371-372`), which also neutralizes the
  `--input-csv` override; full row_gate — required columns, finite d,
  unique case-band keys, exactly-99 paired cases, identical band-2/3 case
  sets, no admitted row outside bands 2 and 3 (`run.py:177-212`).
- **Denominator gates** route zero/nonfinite net, absolute mass, and
  positive mass to the algebra exit, matching the contract's
  algebra/definition failure class (`run.py:267-268, 285-286, 302-303`).
- **Caps and stopping rule.** One variant, zero GPU, one declared-unused
  seed, single pass, immediate stop on any named failure via `fail()`;
  `resolved_config.json` records variants 1 / gpu_minutes 0
  (`run.py:402-407`).
- **Required outputs.** All 14 contract-listed artifacts are written
  (`run.py:373, 380, 411-456`); `split_manifest.csv` and (smoke-only)
  `smoke_input.csv` are extras, permitted. `summary.json` carries
  `idea_id`/`status` and omits `phase`, tolerated under the S2b
  declared-interface ruling.
- **Claim discipline.** Status strings are exactly `CENSUS_COMPLETE` and
  `SMOKE_ONLY`; no directional negative exists anywhere, matching the
  contract's "NO DIRECTIONAL NEGATIVE IS DEFINED"; the plain-language
  template (`run.py:449-455`) claims descriptive accounting only and
  explicitly disclaims stable carriers and population concentration.
  Naming cases in outputs is authorized by v2's `claim_discipline.permitted`.
- **Scope.** The run reads exactly the frozen table and authority metadata:
  no phenotype, reserved-case, image, voxel, or cache access exists in the
  code; `reserved_cases_accessed: 0` is recorded from the split record.
- **Authority convention.** The in-file `human_approved: false` line under a
  fresh marker binding the exact blob is the standing marker-file
  convention, recorded in the v1 round-1 review and the ratified
  interpretation; it carries forward unchanged here.

## Standards checklist (each item verified)

1. **Determinism manifests: MET.** Start manifest written and printed
   (`run.py:373-374`); end manifest recomputed from the same input, compared
   for exact dict equality with a named `EXIT_OUTPUT` failure on divergence,
   then written and printed (`run.py:443-447`).
2. **Exclusions log with reasons: MET.** Every non-admitted row logged with
   `source_line` and reason (`run.py:195, 380`); totals surfaced in
   `summary.json` (see non-blocking finding 1 for the stale comment).
3. **Assertion per transform: MET.** Load (`run.py:198, 210-211`), split
   freeze (`run.py:232-235`), measurement (`run.py:241, 247, 250, 253,
   257`), summaries (`run.py:265, 278-279, 293-296, 311, 339`), manifest
   (`run.py:173`), cross-check of split vs loaded cohort (`run.py:381`).
4. **Declared state: MET.** Seed and paths are top-level annotated constants
   (`run.py:41-55`); the seed is set once and never consumed; no network
   access at analysis time; stdlib only (`requirements.txt`). Two-run byte
   determinism of all scientific outputs attested in `verification.json`.
5. **Split manifest hashed before outcome access: MET.** `freeze_split`
   writes and SHA-256-hashes the anonymous manifest (`run.py:215-236`,
   called at `run.py:369`) strictly before `start_manifest` first opens the
   input CSV (`run.py:370`).
6. **Smoke: MET** (statically; runtime attested by `verification.json`).
   Synthetic 24-case input — at least 20 positives so every frozen top-k and
   both share targets are exercised, plus one zero and three negative
   contributions covering the sign branches; authority check bypassed with a
   non-hex sentinel that cannot masquerade as a blob (`run.py:119-120`);
   status forced `SMOKE_ONLY` (`run.py:398`), which satisfies no contractual
   pattern.

## Practicalities

Runs anywhere with Python 3: stdlib only, no pip installs, `--output-dir`
required with no interactive prompts, default input resolved relative to the
repo root via `__file__`, output directory required empty (compatible with
the driver's blob-scoped output-dir scheme). Sub-second CPU workload; the
5-minute cap is generous.

## Verdict

The census machinery itself is faithful to the frozen preprocessing,
analysis, caps, outputs, and claim discipline, and the smoke/determinism
harness is sound. But the contract's lineage tie to the completed v1 audit —
a named invalidating-failure class with frozen comparison values in the
baselines block — has no implementation, so the one disagreement the
contract singles out as invalidating would today pass silently as
`CENSUS_COMPLETE`. That must be closed before approval; the fix is small,
bounded, and expands no scope.

```json
{"verdict": "REVISE", "blocking": ["B1 (rules 1+2, contract fidelity / silent failure): the v1 lineage-guard comparison required by analysis.secondary_metrics (last item), frozen in baselines[0], and named as a lineage invalidating failure is absent from run.py — recomputed residual, sign/tie counts, cohort counts, and ordering checks are never compared with the completed v1 audit, so a lineage disagreement would emit CENSUS_COMPLETE undetected."], "note": "Faithful census implementation with sound smoke and determinism harness; blocked solely on the unimplemented v1 lineage-guard comparison, which must fail loudly (real mode) and visibly skip (smoke), with the delta-vs-contribution tie-count space named."}
```
