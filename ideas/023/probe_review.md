# Probe code review — idea 023, round 5 (first review of the post-exit-8 amendment revision)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`9978bfed47876ede0aa7f82168bce5382681830855ace4805306893e35451562`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical to the
round-2/3/4 file), `probes/023/README.md` (SHA-256 `1da7fc6e…`), and the
**amended** `ideas/023/probe_contract.yaml` (git blob
`468974a7bdec7a7f6bf869f1520fae101b8d5f27`, file SHA-256 `b164a967…` —
both recomputed this round and matching `probes/023/verification.json`).
Prior approved code: run.py SHA-256 `d2dd41a6…` — verified byte-identical at
both commit `7fbef0e` (the round-4 APPROVE) and commit `6fde01e` (the take-8
launcher commit), so the `6fde01e..681b06c` diff reviewed here is the complete
delta from the last approved artifact. The launcher notebook and
requirements.txt are untouched in `681b06c` (verified by diff stat). Review
rounds 1–4 preserved in git.

**Approval state (deliberate, verified):** `ideas/023/HUMAN_APPROVED_PROBE`
still binds blob `349af5ad…`; the contract is now blob `468974a7…`. The
standing approval is therefore **stale by design**, exactly as the 2026-08-26
amendment directive requires ("the standing approval goes stale by design and
re-approval follows human review of the diff"). The runtime gate
(`run.py:100-123`) compares the marker blob against the live contract blob for
every phase and refuses with exit 2 on mismatch — `verification.json` attests
the builder exercised precisely this refusal. No phase can run until a fresh
marker is bound to `468974a7…`. This review's APPROVE is a recommendation on
the code; the human gate on the amended contract remains controlling.

**Scope note.** This is not a fresh-plan review. The 2026-08-26 decision entry
("023 exit 8: pre-registered unit contingency executed; amendment directive")
authorized a bounded amendment (option B): (1) amend contract clause 66 so the
sole unit-dependent rule becomes unit-free — vessel exclusion = voxels with
CBV above the per-patient 98th percentile of finite positive CBV — recording
in the clause why (the payload evidence) and the conventional-scale
correspondence to the retired 8 mL/100 g cap; (2) update kill-code 104 to mark
the unit-failure contingency executed and retired; (3) clause 72 must not
change; (4) in run.py, implement the percentile exclusion and retire
`confirm_cbv_units` into a recorded finding (`identity.json` gains
`units_documented: false` with the evidence summary); (5) change nothing else.
This review verifies that the contract amendment and the code implement
exactly that directive and nothing else.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist; not a requirements-governed contract. Not applicable.

---

## Disposition of the directive requirements

| Directive item | Status |
|---|---|
| Clause 66 amended to the unit-free percentile rule, with the why and the conventional-scale note | **Resolved** — contract line 66 (`preprocessing.region`) now reads "voxels with CBV above the per-patient 98th percentile of finite positive CBV in that patient's map", records the evidence (zero JSON sidecars, empty NIfTI descrip fields, no inspected dataset descriptor states units) and states that under the conventional scale the percentile targets approximately the vessel fraction the 8 mL/100 g cap intended — the directive's three required elements, verbatim in spirit |
| Kill-code 104 marked executed and retired | **Resolved** — the former "Unit failure" invalidating-failures entry is replaced by "Retired contingency (formerly kill-code 104): undocumented CBV units triggered the preregistered stop before outcomes were read; this amendment executes and retires that unit-failure path…" (contract line 104) |
| Clause 72 unchanged | **Resolved** — contract line 72 is `joint_state` (the median-centered central-volume coordinate, unit-robust by construction); the contract diff touches exactly two lines, 66 and 104, and nothing else |
| run.py implements the percentile exclusion | **Resolved** — `coordinate_arrays` (`run.py:494-536`): `positive_cbv = cbv[np.isfinite(cbv) & (cbv > 0)]` over the whole patient map, `vessel_cbv_p98 = np.percentile(positive_cbv, 98.0)`, `vessel = np.isfinite(cbv) & (cbv > vessel_cbv_p98)` — per-patient, finite-positive support, strict "above", matching clause 66 word for word; an all-nonpositive CBV map fails loudly (exit 6, grid/data class) instead of producing a degenerate threshold, and an assertion pins the threshold finite and positive |
| `confirm_cbv_units` retired into a recorded finding | **Resolved** — the function and its sole call site are deleted; `fail(8` has zero remaining occurrences (grep-verified), the docstring relabels exit 8 "retired unit contingency", and `phase_c_cache/identity.json` (the file the directive names) gains `units_documented: false` plus `units_evidence` summarizing exactly the exit-8 receipt's evidence (`run.py:685-689`) |
| Change nothing else | **Resolved** — the full run.py diff touches only: the docstring exit-code line, the Phase-C section comment, the `confirm_cbv_units` deletion (definition + call), the percentile block in `coordinate_arrays`, the `vessel_cbv_p98` audit value in the per-case exclusions dict and the `exclusion_fields` column list, and the two identity keys. Phase S, the approval gate, provenance/census/split logic, all strata, gates, thresholds, the bootstrap, the three-stratum conjunction, statuses, and the stopping rule are byte-unchanged; requirements.txt and the launcher are byte-unchanged |

Two additions sit slightly beyond the directive's letter and are judged inside
its intent rather than scope creep: the per-patient `vessel_cbv_p98` recorded
in `exclusions.csv` (the audit trail the exclusions-with-reasons standard
requires for a rule that now varies per patient — without it the realized
thresholds would be unrecoverable), and four README lines documenting the
amendment (matching the round-3 precedent that the README states what the
contract requires). Neither changes any measurement.

## Validation details (this round's decisive checks)

- **Unit-freedom is real, not asserted.** The percentile mask is invariant
  under any global positive rescaling of CBV (p98 scales linearly; `cbv >
  p98` is unchanged), rCBF/rCBV are mirror ratios, and the identity residual
  is census-median-centered (clause 72) — so no quantity anywhere in Phase C
  now depends on the undocumented CBV unit. The builder's fixture attests
  this concretely: "sevenfold CBV/MTT rescaling preserved the percentile
  vessel mask", alongside a fixture matching numpy's p98 and exact strict-
  above selection (`verification.json`).
- **Label-blindness preserved.** The percentile is computed inside the
  label-blind map pass (`load_case(..., load_label=False)` at `run.py:705`,
  before any lesion is opened) and depends only on the patient's own CBV map;
  the split freeze and hash still precede all lesion access. No label can
  influence the new exclusion.
- **Consistent use at both sites.** The same `vessel` mask feeds both the
  mirror-median `allowed` set (`brain & ~deficit & ~vessel`, matching clause
  67 "after excluding deficit and vessel voxels") and the analysis-region
  exclusion (`eroded &= brain & ~vessel & valid_den & finite_maps`), exactly
  as the fixed 8 mL/100 g mask did before — only the threshold definition
  moved, not where it applies.
- **Checkpoint supersession is enforced.** The identity dict now differs from
  any pre-amendment cache in four ways (contract blob, run.py SHA-256, and
  the two new unit keys), so no checkpoint written by superseded code can be
  honored; the mismatch path fails closed at exit 4 (`run.py:690-691`).
- **Historical references are history only.** The only remaining mentions of
  the 8 mL/100 g cap are comments explaining the amendment's provenance —
  which the directive explicitly asked to be recorded — not live thresholds.

## Round-4 finding disposition

- **N4 (unit gate may stop the run): closed — executed as designed.** The
  contingency fired in take 8 exactly as preregistered, before outcomes were
  read, and is retired by this amendment. This was the system working.
- **R4 (verification.json lost the marker-binding attestation): resolved** —
  the rebuilt file records `approval_status:
  STALE_BY_DESIGN_PENDING_HUMAN_REAPPROVAL`, the new contract blob, all four
  artifact hashes (each matching my recomputation), and an executed check
  that Phase C refuses with exit 2 under the stale marker.
- **R1 (README duplicate-handling sentence mispredicts the real payload):
  carried, deliberately.** The paragraph (`README.md:33-36`) still describes
  only the byte-identical-lexicographic fallback and the loud stop, omitting
  the canonical `space-ncct` schema-position rule that actually resolves
  sub-stroke0142's non-identical duplicate. The generator obeyed the
  directive's "change nothing else" over round 4's fix-at-next-touch note —
  the defensible reading of the narrower, later instruction — but the fix
  remains outstanding for the next authorized touch.
- **F1 (quartile-cut vs measurement mask), F2 (outcome checkpoint rewrite
  not atomic), F4b (permitted nonfinite lesion values excluded but not
  counted), F5 (conceptrecid lineage not pinned), F7 (all-empty coordinate
  reaches exit 13), R2 (lowercase ids vs case-sensitive glob), R3 (orphan
  lesion hard stop), N6–N9: all carried byte-unchanged**, per the directive's
  no-other-changes rule. None is blocking; none is touched by the amendment.

## Blocking findings

None.

## Non-blocking findings (new this round)

**R5 — The take-8 stale cache will trip exit 4 if the same output directory
is reused, and the message still does not name the remedy (F6, now live).**
Take 8 wrote `phase_c_cache/identity.json` (old blob, old run.py hash, no
unit keys) before stopping at exit 8. A take-9 rerun pointed at the same
`--output-dir` will fail closed at `run.py:690-691` — correct in direction,
since pre-amendment checkpoints must not be honored — but the operator-facing
message still omits the fix (delete `phase_c_cache/` or use a fresh output
dir). Fold the remedy into the message, or clear/redirect the cache at
launch, whenever run.py is next authorized for touch.

**R6 — The recorded units finding lives only in the cache directory and the
README.** The directive named `identity.json`, and the code is faithful to
it; but `summary.json` and `provenance.json` (the required-outputs bundle)
do not echo `units_documented: false`, so a results bundle that omits
`phase_c_cache/` would not carry the finding of record. A one-key echo into
`summary.json` at the next authorized touch would make the bundle
self-contained. Not a directive violation.

**R7 — Strict "above" plus heavy value ties could exclude less than 2% of
voxels.** With a quantized CBV map, `cbv > p98` may exclude far fewer than
2% of positive voxels (ties at the threshold are retained). This is the
verbatim contract semantics ("above the … percentile"), deterministic, and
recorded per patient via `vessel_cbv_p98` and `vessel_voxels`, so any
anomaly is visible in `exclusions.csv`; noted so a low realized exclusion
fraction is read as tie behavior, not a fault.

## Verified correct (spot-checked this round)

- **Gate mechanics:** marker/contract blob binding enforced for both phases;
  the frozen Phase-S thresholds (N=20, M=100, width 0.15) and
  `simulation_output_sha256` still read from the contract, never hardcoded;
  `--phase-s-dir` remains required for Phase C with the simulation hash
  verified before any record/archive/image access; placeholder scan, no-test
  path guard, and code/contract drift checks unchanged.
- **Analysis discipline unchanged:** equal patient weight, single
  `default_rng(20260824)` stream, 2000-resample patient bootstrap,
  direction-aware three-stratum conjunction, support shortfall exit 10
  (invalidating, never a negative), one variant, one seed, zero GPU, no
  pooled fallback; result statuses remain exactly the contract's
  `POSITIVE_PATTERN`/`NEGATIVE_PATTERN` language and the closing
  interpretation still forbids physiological and model-use claims.
- **Audit outputs:** `exclusion_fields` declares the new column explicitly;
  duplicate-lesion rows take DictWriter restval for it, analyzed-case rows
  carry the realized threshold; no undeclared-key `ValueError` path.
- **Standards checklist:** (1) determinism manifests present and agreeing
  (`resolved_config.json` and `summary.json` sections byte-unchanged from
  the approved code); (2) exclusions log with reasons — strengthened by the
  per-patient threshold; (3) assertion per transform — the new p98 assert
  joins the unchanged split/grid/mirror/identity assertions; (4) seeds and
  paths declared, no analysis-time network; (5) split manifest hashed before
  any lesion access, and the new computation is label-blind; (6) `--smoke`
  synthetic-only and reporting `contract_satisfied: false`, attested by the
  rebuilt `verification.json` whose artifact hashes match the reviewed
  files. As in rounds 3–4, this environment cannot execute Python, so
  executed-check attestations plus static tracing are the basis.

## Verdict

The amendment is implemented exactly and minimally: two contract lines (the
unit-free percentile rule with its recorded evidence, and the retired
kill-code-104 contingency), a 41-line run.py delta that deletes the units
gate, computes the per-patient p98 label-blind, applies it at both sites the
old cap applied, and records the units finding in `identity.json` verbatim
per the directive — with Phase S, the split, all gates, thresholds, and the
analysis byte-unchanged and clause 72 untouched. The whole Phase-C pipeline
is now demonstrably invariant to the undocumented CBV unit. The approval
marker is stale by construction; nothing can run until the human reviews the
contract diff and binds a fresh approval to blob `468974a7…`. Three new
findings are operational polish; none changes what the census measures.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Exit-8 amendment directive implemented exactly (unit-free per-patient p98 vessel exclusion, units gate retired into identity.json, clauses 66/104 amended, clause 72 and all analysis untouched); approval stale by design pending fresh human binding to contract blob 468974a7; three non-blocking operational findings."}
```
