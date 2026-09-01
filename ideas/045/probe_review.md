# Probe code review — idea 045, contract v3 (attribution analysis), round 1

Artifacts reviewed: `probes/045/run.py` (committed 720aecc, sha256
`69622688fd247862606a34a34b5633517d18b749765ce3a5e740f9202f579a90`, recomputed
during this review), `probes/045/requirements.txt`, `probes/045/README.md`,
`probes/045/verification.json`, against `ideas/045/probe_contract.yaml` v3
(blob `b1e283613d4fd47c77bfd1f2838a54791eb25954`, recomputed this round and
verified equal to the `HUMAN_APPROVED_PROBE` marker binding of
2026-09-01T06:57:20Z; the marker also pins registry sha `1c0e82a6…`) and
`ideas/045/feasibility.md`. There is no `contract_requirements.md` in
`ideas/045/`, so criterion 5's requirements-governed checks do not apply.

This contract is qualitatively different from the two executed feasibility
probes: it authorizes reading the outcome column `d` for the first time in
this lineage. The review therefore concentrated on outcome-access ordering,
the frozen interpretation rules, and every surface where an unauthorized
analysis or a silently degraded bootstrap could leak in.

Method note: this environment blocks arbitrary process execution, so the
smoke run was not re-executed here. Smoke evidence is the committed
verification receipt — now the rich format the v2 review asked for —
recording compile pass, smoke exit 0 with status `SMOKE_ONLY` in 1 second,
missing-input exit 3, output-collision exit 7, split-written-before-outcome
true, determinism-manifest equality, and binding both `run_py_sha256`
`69622688…` (matches the working tree exactly) and the approved contract
blob, checked at 2026-09-01T07:01:45Z — after the 06:57:20Z approval and in
the same commit as the reviewed `run.py`. Input identities and structure
were re-derived directly from the two CSVs during this review (hashes and
per-stratum counts below); no observed `d` value was read.

## Contract fidelity — verified

**Approval gate.** `verify_authority` (run.py:128-155) requires the marker
and contract, extracts `contract_blob`, recomputes the live contract's git
blob, and refuses on mismatch (exit 2). The literal-drift guard checks nine
v3 literals — `contract_version: 3`, the exact 10,000-replicate and seed
20260901 phrasing, all three caps, and all three status names — and each was
confirmed present in the approved contract bytes during this review
(contract lines 6, 58, 79-81, 66/85/86).

**Input identity now enforced in-run.** The v2 review's leading non-blocking
finding is closed: non-smoke runs recompute both input SHA-256s and refuse
on any mismatch with the frozen pins (run.py:472-475, exit 3), and
reserved/test-looking paths are refused outright (467-469). Both pins were
re-verified on disk this round: `bin_tissue_audit.csv` = `35e896df…`,
`per_patient.csv` = `1d01551c…`, exactly the contract's `frozen_inputs`.

**Split before outcome access.** `freeze_split` (227-259) derives the
198-row split from the label-blind audit alone, writes `split_manifest.csv`,
and hashes it (249) — all at call site 477, before `load_outcomes` first
opens `per_patient.csv` at 484. `d` is parsed nowhere before that point.

**The design matrix is exactly the authorized one.** Intercept, band-3
indicator, pooled-mean-centered HU imbalance (362-367, shape-asserted
(n, 3)); imbalance is Q1 minus Q4 median HU by direct subtraction (327); no
interaction, transform, winsorization, ranking, binning, subgroup, or
covariate exists anywhere in the file. Centering is the pooled mean over the
analysis rows, the v2 rule.

**Estimator and reported quantities.** One OLS fit via `lstsq` with rank and
finiteness refusals (372-376). The ten-element metric vector (390-395) maps
one-to-one onto the contract's primary and secondary metrics: beta_HU;
adjusted band-2 mean (intercept), adjusted band-3 mean (intercept + band
coefficient), adjusted difference (= band coefficient); equal-patient-weight
unadjusted band means computed directly from the raw rows (387-388 — each
patient contributes exactly one row per band, so this is the
equal-patient-weight mean, and no second model is fit, satisfying baseline 3
in its narrowest form); unadjusted difference; per-band
adjusted-minus-unadjusted changes; and the absolute-band-difference change.
Per-patient fitted values, residuals, and hat leverage from the single
authorized fit go to `per_patient_attribution.csv` (526-529).

**Parent-reconstruction gate.** Non-smoke, before any bootstrap cost is
spent: unadjusted band-2 mean must be negative and band-3 positive or the
run refuses with exit 5 and no scientific reinterpretation (506-507). Row
counts are enforced at exactly 99 cases per band by the join (320-321), with
bidirectional key-set equality across audit, outcome, and frozen split
(313-316) and per-case Q1/Q4 cell completeness (323-326).

**Bootstrap exactly as contracted.** Exactly 10,000 replicates non-smoke
(508, constant at 49); seed 20260901 via `np.random.default_rng` (404);
resampling draws 99 patients with replacement and both band rows travel
together (409-410, with an assert that every case holds exactly 2 rows,
403); the same frozen model is refit per replicate; intervals are percentile
[2.5, 97.5] (425-428). Failure handling implements the contract's rule in
its strongest form: any replicate that raises or yields a nonfinite metric
vector aborts the run with exit 6, naming the replicate (412-417) — no
replicate can be silently dropped, so a completed bundle can only ever carry
`failed_replicates: 0`.

**Interpretation rule mapped exactly, with correct precedence.** `classify`
(431-443): smoke → `SMOKE_ONLY` unconditionally; DECISIVE requires the
adjusted band-2 interval entirely below zero AND band-3 entirely above zero;
ASSOCIATION requires beta_HU's interval to exclude zero AND the decisive
conjunction broken (evaluated only after decisive fails, so a precise slope
cannot override an intact reversal); everything else is
`SENSITIVITY_LIMITED`. `summary.json`'s `opposite_sign_precise` uses the
identical conjunction (558-561).

**Caps and stopping rule.** One variant (single fit + its bootstrap; logged
`Variant 1/1`, 459; recorded `variants_run: 1`); one seed; zero GPU; zero
network (no network-capable import; `network_calls: 0` recorded). The
30-minute wall cap is enforced inside the bootstrap loop (407-408) — the
only phase that can run long — and a wall-time stop is exit 8 with no
`summary.json` written, so it is structurally incapable of being read as a
negative, exactly as the contract requires.

**Required outputs.** All nine contract-required artifacts are written:
resolved_config.json (577), input_manifest.csv (496), exclusions.csv (487),
per_patient_attribution.csv (529), model_diagnostics.json (538),
bootstrap_summary.json (545), summary.json (568), environment.txt (583),
run_log.txt (592) — plus split manifests and both determinism manifests.

**Lineage.** Nothing reads or writes `results_v2/` or `results_v3/`; the v2
baselines cited in the contract are lineage evidence and are correctly not
recomputed or compared in-run. `prepare_output_dir` (158-163) refuses any
output directory already containing scientific outputs, closing the v2
review's collision finding — pointing `--output-dir` at either historical
bundle now refuses with exit 7.

**Input structure re-derived on disk this round.** Audit: 594 data rows, 198
per stratum, primary bands exactly 297 `Q1_low_CBV` + 297 `Q4_high_CBV`
rows, zero duplicate (case, stratum, style) keys. Outcome: 297 rows, 99 per
stratum, zero duplicate (case, stratum) keys. Expected real-run accounting
is therefore audit 594 → 396 selected + 198 excluded, outcome 297 → 198 +
99 excluded, total 297 exclusions — which is precisely the conservation
assert at 489 (594 + 297 − 198×3).

## Standards checklist — all six MET

1. **Determinism manifests** — start manifest written and printed before
   measurement (490-494); end manifest recomputed at 584 including
   re-hashing both input files, compared for exact equality with classified
   exit 7 (586-587), then written and printed.
2. **Exclusions log with reasons** — per-row records with source, line,
   case, stratum, and reason `non_primary_band` (215-217, 280-282, 487-488);
   conservation assert (489) verified against the real input structure
   above.
3. **Assertion per transform** — loaders (220-221, 294-295), split (238-239,
   244, 258), join (311, 328, 333-334), fit (369-371, 380-381, 389, 396),
   bootstrap (403, 411, 421), intervals (427).
4. **Declared state, no hidden state or network** — every scientific
   constant declared with contract provenance (46-64); seeds set (450-451);
   no network access anywhere; inputs, outputs, and paths all surfaced in
   resolved_config.
5. **Split-before-outcome** — split written and sha256-hashed (245-257) at
   477 before the outcome file is first opened at 484. In smoke mode the
   fixture is *written* earlier but the split still precedes the only
   *read*.
6. **Smoke** — receipt shows 1-second completion; structurally unable to
   satisfy any contractual gate three ways: `classify` returns `SMOKE_ONLY`
   before any rule is evaluated (432-433), the 12-case fixture cannot pass
   the 99-case cohort join outside smoke's own expected count, and
   `verify_authority` returns a non-blob sentinel recorded in
   resolved_config, so a smoke bundle can never present as approval-bound.

## Silent-failure surfaces — clean

Missing files, empty CSVs, missing columns, nonnumeric fields, nonfinite
values, duplicate keys, unknown styles, key-set mismatches, and band-count
errors all refuse with classified exits; the nonnumeric-field taxonomy
quibble from the v2 review is fixed (schema drift now exits 3, the input
class). The only try/except blocks are the two loader field-parsers (which
re-raise as classified failures), the bootstrap replicate wrapper (which
converts any failure into an invalidating exit 6), and the top-level
classifier, which prints the full traceback for unexpected faults (615-617).
A broken input cannot print a number.

## Claim discipline — clean

Status vocabulary is exactly the contract's three classes plus `SMOKE_ONLY`
(439-443); the printed templates (596-601) track the contract's
positive/negative/third-outcome language including the mandatory scope
guards ("no broader tissue-composition claim follows", "observational
compatibility with contribution, not causation", "not evidence of no
association or independence"). No stronger sentence appears anywhere in
run.py or the README. No analysis beyond the contract is reachable: band 1
is excluded at load, reserved cases are physically absent from the pinned
inputs and guarded twice anyway, and no second model, threshold, or variant
exists.

## Readability — good

Accurate module docstring with the model, the three outcome classes, run
commands, and a full exit-code table (2-26); four narrated phase comments;
constants annotated with contract provenance; bootstrap progress every 10%;
plain-English interpretation template at the end. The README gives the
one-line command and correctly warns off the historical output directories.

## Practicalities — will run

`numpy==2.5.2` pinned (matching the verification environment, and nailing
the bootstrap draw stream against numpy Generator-stream drift); paths are
repo-relative from `__file__`; `--output-dir` is required with no
interactive prompts; CPU-only, minutes-scale (receipt: smoke in 1 s; the
real run is 10,000 trivial 198×3 fits). Nothing Colab-specific is needed —
this is the laptop-scale probe the feasibility memo described.

## Non-blocking findings

1. **Per-replicate re-centering — recorded now, before outcomes are seen.**
   `fit_model` recomputes the pooled centering mean within each bootstrap
   replicate (364, via 413), so the bootstrap resamples the full plug-in
   functional ("adjusted band mean at that resample's pooled-mean
   imbalance") rather than freezing the full-data centering constant. The
   contract underdetermines this ("refit the same frozen model"; centering
   "using the same centering rule as v2"), and the code's choice matches
   both textbook pipeline bootstrapping and the lineage convention — the v2
   contract's leave-one-patient-out diagnostic explicitly recomputed pooled
   centering within each deletion. beta_HU and the band coefficient are
   centering-invariant; only intercept-type draws shift, by beta_HU times
   the (small) replicate-center deviation. This is the right implementation;
   it is recorded here so the interpret stage describes the CI functional
   accurately and so no post-hoc relitigation of the choice can occur after
   the result is visible.
2. **Interval-position formalization of the decisive rule.** The contract's
   "remains below/above zero and both intervals exclude zero" is
   implemented as the interval lying entirely on the required side (437) —
   the natural formalization; point-estimate signs are not separately
   tested. For a 10,000-draw percentile interval of a smooth functional the
   two cannot realistically diverge; noting for completeness.
3. **`failed_replicates: 0` is a structural constant on the success path**
   (541): any replicate failure aborts the run, so a nonzero count can never
   coexist with a written bundle. This satisfies the contract's
   "any count above zero is invalidating" in its strongest form; the
   recorded field is truthful but is an invariant, not a measurement.
4. **`verify_authority` is skipped entirely under `--smoke`** (129-130),
   returning a sentinel recorded in resolved_config. Smoke is therefore
   runnable pre-approval (the v2 probe's smoke ran the gate). Acceptable —
   smoke uses synthetic fixtures, is always `SMOKE_ONLY`, and cannot
   masquerade as approval-bound — but the asymmetry is worth the record.
5. **Collision guard checks only the target directory itself** (160-163). A
   pathological `--output-dir` naming a NEW subdirectory inside a governed
   bundle (e.g. `probes/023/results/results_v2/x`) would create files
   inside an imported bundle tree. Much narrower than the v2 finding it
   descends from (direct overwrite now refuses), mitigated by the README's
   explicit instruction, the driver's output-dir policy, and git
   visibility; an ancestry check would close it fully.
6. **`run_log.txt` written on the success path only** (592; carried from
   v1/v2). Failures still persist forensics via stderr.
7. **Status names vs importer conventions (ops note, S2b lineage).** The
   bundle's `status` values are the contract's own three classes, not the
   older `POSITIVE_PATTERN`/`NEGATIVE_PATTERN` literals; contract-faithful
   and correct, but the idea-045 registry currently declares no v3 node, so
   the node added at import time must declare these three terminal statuses,
   and the record-result lane should expect them. Flagging so the interface
   hydra's third head is anticipated rather than discovered.
8. **Cosmetics:** `environment.txt` contains JSON despite its extension
   (carried; the contract names the file); `summary.json`'s `unique_cases`
   echoes the expectation constant rather than a recount (the join asserts
   equality first, so it is truthful); `prepare_output_dir` runs before
   `verify_authority`, so an unapproved invocation creates an empty
   directory before refusing.

## Verdict

The code implements exactly the approved v3 contract: the one authorized
model on the two pinned inputs with in-run hash enforcement, split frozen
and hashed before the first outcome read, the exact 10,000-replicate
seed-20260901 patient-cluster bootstrap with abort-on-any-failure
semantics, the three frozen interpretation classes with correct precedence,
all nine required outputs, and both v2 non-blocking hardening items closed
(input-pin enforcement, output-collision refusal). All six hard standards
are met; no blocking finding exists under any review rule.

```json
{"verdict": "APPROVE", "blocking": [], "note": "v3 code is contract-exact: pins enforced in-run, split frozen before first outcome read, 10k-replicate seed-20260901 cluster bootstrap with abort-on-failure, frozen three-class rule with correct precedence; all standards met, both v2 findings closed."}
```
