# Probe code review — idea 023, round 6 (first review of the post-take-11 dual-directive revision)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`acae802f0ae502eda9e9e8a594fe76c9998a8b3ca09672cdff83a7f3fcc6e02b`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical to the
rounds-2-through-5 file), `probes/023/README.md` (SHA-256 `86a67ada…`), and
the **amended** `ideas/023/probe_contract.yaml` (git blob
`2963f66b018a28eee22f49bfeb928a62e5bc9530`, file SHA-256 `07fe0c41…`). All
four hashes recomputed this round and matching `probes/023/verification.json`.
Prior approved code: run.py SHA-256 `9978bfed…` — verified byte-identical at
commit `df8f748` (the parent of the revision commit), and the contract there
is blob `468974a7…`, so the `df8f748..e7798f3` diff reviewed here is the
complete delta from the last approved artifacts. The launcher notebook and
requirements.txt are untouched in `e7798f3` (verified by diff stat). Review
rounds 1–5 preserved in git.

**Approval state (deliberate, verified):** `ideas/023/HUMAN_APPROVED_PROBE`
binds blob `468974a7…` (the post-exit-8 approval of 2026-08-25 under which
takes 9–11 ran); the contract is now blob `2963f66b…`. The standing approval
is therefore **stale by design**: the take-11 directive said "If the reviewer
judges (a) to require a contract amendment (cohort/selection language), author
the amendment in the same round" — probe-build judged yes and authored it, and
the amendment stales the approval by construction. The runtime gate
(`run.py:116-140`) compares marker blob against live contract blob for every
phase and refuses with exit 2 on mismatch; `verification.json` attests the
builder exercised precisely this refusal ("Phase C refused with exit 2 while
the approval marker is stale"). Nothing can run until a fresh marker is bound
to `2963f66b…`. This APPROVE is a recommendation on the code; the human gate
on the amended contract remains controlling.

**Scope note.** This is not a fresh-plan review. The 2026-08-26 decision entry
("023 take 11: SOURCE data defect proven; paired-run plan superseded; dual
directive") authorized exactly two changes: **(a)** a case whose required
input is a source-defective member (unreadable gzip from the verified archive)
routes to `exclusions.csv` with reason `source_corrupt_member` naming the
file, and the map pass continues, with the summary and interpretation
surfacing the excluded count; **(b)** stratum admission additionally requires
finite rCBF and rCBV (the pre-registered finiteness tightening, folded into
this single canonical run by the take-11 supersession). Change nothing else.
This review verifies the contract amendment and the code implement exactly
that directive and nothing else.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist (verified this round); not a requirements-governed contract.
Not applicable.

---

## Disposition of the directive requirements

| Directive item | Status |
|---|---|
| Contract amended for the exclusion, if the reviewer judges it required | **Resolved, and I concur it was required** — the prior `invalidating_failures` population clause made "missing required maps or label for a census patient" invalidating, which would have collided with any exclusion of sub-stroke0043. The amendment touches exactly two lines: `dataset.required_inputs` (naming the one verified defective member — `train/derivatives/sub-stroke0043/ses-01/perfusion-maps/sub-stroke0043_ses-01_space-ncct_cbf.nii.gz`, CRC-valid, unreadable gzip — with the exclusion, naming, continue, and surface obligations, and the fail-loud rule for any other member) and the population-failure clause (now "(distinct from a present source_corrupt_member handled by dataset.required_inputs)"). Nothing else in the contract moved (verified by full diff) |
| (a) exclusion routed, member named, map pass continues | **Resolved** — `SOURCE_CORRUPT_MEMBERS` (`run.py:63-67`) is a one-member tuple naming exactly the contract's member; `verify_required_gzip` (`run.py:319-331`) reads every required `.nii.gz` stream fully; in the map pass, `SourceCorruptMember` from `load_case` yields an `EXCLUDE` log line, a `schema_census.csv` row (`record_type=excluded_case`, `exclusion_reason=source_corrupt_member`, files JSON carrying the exact path), an `exclusions.csv` row (`reason`, `source_path`), and `continue` (`run.py:750-763`); the outcome pass skips excluded cases (`run.py:850-852`); both audit CSVs are rewritten after the outcome pass (`run.py:888-891`) |
| (a) any other unreadable member fails loudly | **Resolved** — for a path not ending in a `SOURCE_CORRUPT_MEMBERS` entry, `verify_required_gzip` calls `fail(6, "unreadable required gzip is not the preregistered source defect…")`; a *missing* member still exits 5 via `find_one` (`run.py:237-239`), matching the contract's "present source_corrupt_member" distinction. The exclusion cannot silently widen |
| (a) summary and interpretation surface the excluded count | **Resolved for this probe's outputs** — `summary.json` gains `excluded_source_corrupt_cases` and `analyzed_census_case_count` (`run.py:919,922`), and the full summary is printed as the run's final output (`run.py:955`); the README states the behavior. The interpret-stage obligation is carried forward by the decision ledger, not dischargeable by run.py |
| (b) stratum admission requires finite rCBF and rCBV | **Resolved** — both and only the two stratum-mask sites in the file (grep-verified) gain `finite_ratios = np.isfinite(rcbf) & np.isfinite(rcbv)`: the label-blind quartile pass (`patient_native_z`, `run.py:576-582`) and the outcome pass (`patient_measure`, `run.py:594-598`), with an assertion at each site. The rule is identical in both passes, so quartile cuts and outcome contributions see the same admission set; no stratum boundary changed. No contract amendment was needed for (b): the directive routed it as a code change, and it enforces the contract's own finiteness spirit (grid_gate; clause 72's `z = log(rCBV)` is not a coordinate at infinity). This closes the take-10 overflow edge: an infinite rCBV from a tiny positive mirror denominator that passes `valid_den` can no longer enter `log(rcbv)` |
| Change nothing else | **Resolved** — the complete run.py diff contains only: the `gzip`/`zlib` imports, the constant and exception class, `verify_required_gzip`, the `load_case` verification loop, the two mask lines plus asserts, the `load_lesion` verification call, the exclusion handling in both passes, the post-outcome rewrite of the two audit CSVs, and the two summary keys. Phase S, the approval gate, provenance/census/split logic, mirror QC, the identity residual, quartile estimation, the bootstrap, the three-stratum conjunction, all thresholds, statuses, and the stopping rule are byte-unchanged; requirements.txt and the launcher notebook are byte-unchanged |

## Validation details (this round's decisive checks)

- **The exclusion is deterministic under resume.** sub-stroke0043 can never
  acquire a checkpoint (`load_case` raises before `atomic_npz`), so every
  fresh or resumed run re-derives the exclusion identically;
  `excluded_source_cases` is rebuilt in memory each run, checkpoint-hit rows
  are rebuilt from the per-case audit JSONs (`run.py:741-785`), and the final
  CSV rewrite is therefore complete on any run shape.
- **Chain consistency with the take-11 launcher.** The launcher's integrity
  sweep now tolerates-and-announces `SOURCE_MEMBER_DEFECT` for stored-CRC-valid
  members that fail gzip, so the defective file lands on disk; `find_one`
  resolves it (it is present), and `verify_required_gzip` is what makes the
  census confront it. The probe does not depend on the launcher's
  classification: even if a future staging path delivered a different
  unreadable member, run.py exits 6 rather than excluding.
- **Gate arithmetic under one exclusion.** The mirror gate's absolute
  threshold (≥90 census patients) and the Phase-S-frozen support minimum
  (N=20 per stratum) are unchanged and remain satisfiable from 99 analyzed
  patients; the exclusion is the contract-authorized path, and
  `analyzed_census_case_count` records the reduction. No operating
  characteristic was re-derived, correctly — the contract froze them and the
  amendment did not touch them.
- **Label-blindness preserved.** The new full-stream reads in pass one touch
  maps and NCCT only (`load_case` is called with `load_label=False`); the
  lesion stream is read only in pass two, after the split hash and quartile
  cuts are frozen. The new exclusion depends on gzip readability, never on any
  label value.
- **Finiteness tightening is total where it matters.** Within the tightened
  masks, `z = log(rcbv)` and the identity coordinate are finite by
  construction (finite positive inputs; region already requires finite raw
  maps), so no nonfinite value can reach quartile estimation, the identity
  gate, or a patient's `d`.

## Round-5 finding disposition

- **R5 (stale take-8 cache trips exit 4 without naming the remedy):
  substantially mitigated upstream** — the take-9 launcher change blob-scopes
  `OUTPUT_DIR`, so each contract era gets a pristine cache directory; the
  message-text improvement remains on the polish list.
- **R6 (units finding lives only in `identity.json` and the README): carried
  byte-unchanged** — `summary.json` still does not echo
  `units_documented: false`; the one-key echo remains recommended at next
  authorized touch.
- **R7 (strict-above percentile tie behavior): carried**, unchanged semantics,
  still auditable per patient via `vessel_cbv_p98`.
- **R1 (README duplicate-handling sentence mispredicts the real payload):
  carried a third round, now adjacent to new text.** The paragraph
  (`README.md:33-36`) still describes only the byte-identical-lexicographic
  fallback and says non-identical duplicates stop as a population failure,
  omitting the canonical ses-2 schema-position rule that actually resolves the
  payload's real non-identical duplicate. The generator again obeyed "change
  nothing else" — defensible — but the README was touched this round four
  lines below the stale sentence. Fix at the next authorized documentation
  touch.
- **F1 (quartile-cut vs measurement mask asymmetry — the `cbf/cbv/mtt > 0`
  terms appear only in the label-blind mask): carried**; the finiteness
  tightening was added symmetrically to both masks and neither widened nor
  narrowed this pre-existing delta. **F2 (outcome checkpoint rewrite not
  atomic), F4b (permitted nonfinite lesion values excluded but not counted),
  F5 (conceptrecid lineage not pinned), F7 (all-empty coordinate reaches exit
  13), R2 (lowercase ids vs case-sensitive glob), R3 (orphan-lesion hard
  stop), N6–N9: all carried byte-unchanged**, per the no-other-changes rule.
  None is blocking; none interacts with this amendment.

## Blocking findings

None.

## Non-blocking findings (new this round)

**R8 — Voxels removed by the finiteness tightening are not counted in
`exclusions.csv`.** The overflow voxels this rule targets pass `valid_den`
(tiny positive denominator), so they are absent from
`invalid_or_nonpositive_denominator_voxels`, and no `nonfinite_ratio_voxels`
column exists. Because the take-11 supersession folded the pre-registered
paired-run comparison into one canonical run, a per-case count is the only
cheap way for the interpret stage to gauge the tightening's materiality; today
that number is recoverable only from the persisted `phase_c_cache` npz files
(`rcbf`, `rcbv`, `region` are checkpointed). Consistent with the carried F4b
precedent this is non-blocking, but a count column is recommended at the next
authorized touch.

**R9 — The outcome-pass `SourceCorruptMember` handler (`run.py:864-876`) is
unreachable with the current one-member tuple.** The preregistered member is a
CBF file consumed in pass one; an unreadable lesion stream exits 6 because its
path cannot match the tuple. The branch is deliberate generality (the comment
says a defective *label* member would be retained if one were ever
preregistered) and is correct in direction, but it is untested dead code today;
its `next(...)` would surface as exit 13 if no `analyzed_case` schema row
existed. Note only.

**R10 — Any `OSError` on the preregistered path is attributed to the source
defect.** A transient I/O fault on exactly that one file would be recorded as
`source_corrupt_member` rather than a harness fault. The scope is a single
twice-proven-defective file read from local SSD, and the misattribution risk
is negligible; recorded so the classification boundary is on the record.

**R11 — Cosmetic:** the mirror-gate failure message hardcodes a `/100`
denominator (`run.py:803`) while at most 99 patients can now contribute mirror
rows. The gate's absolute ≥90 threshold is contract-faithful and unchanged.

## Verified correct (spot-checked this round)

- **Gate mechanics:** marker/contract blob binding enforced for both phases
  with exit 2; frozen Phase-S values (N=20, M=100, width 0.15) and
  `simulation_output_sha256` still read from the contract, never hardcoded;
  `--phase-s-dir` still required for Phase C; placeholder scan and
  code/contract drift checks unchanged.
- **Analysis discipline unchanged:** equal patient weight, single
  `default_rng(20260824)` stream, 2000-resample patient bootstrap,
  direction-aware three-stratum conjunction, support shortfall exit 10
  (invalidating, never a negative), one variant, one seed, zero GPU; result
  statuses remain exactly the contract's `POSITIVE_PATTERN`/`NEGATIVE_PATTERN`
  language and the closing interpretation template still forbids physiological
  and model-use claims.
- **Audit outputs:** `exclusion_fields` and `schema_fields` declare the
  routing columns (`record_type`, `reason`/`exclusion_reason`, `source_path`);
  the new rows' keys are all declared (no undeclared-key `ValueError` path);
  analyzed-case rows still carry the per-patient `vessel_cbv_p98`.
- **Standards checklist:** (1) determinism manifests present and agreeing
  (`resolved_config.json`, `provenance.json`, `summary.json` mechanisms
  byte-unchanged); (2) exclusions log with reasons — strengthened by the named
  source-path rows (R8 notes one uncounted voxel class); (3) assertion per
  transform — the two new admission asserts join the unchanged
  split/grid/mirror/identity assertions; (4) seeds and paths declared, no
  analysis-time network (the new reads are local files already required);
  (5) split manifest hashed before any lesion access, and the new pass-one
  reads are label-blind; (6) `--smoke` remains synthetic-only, cannot invoke
  any of the new code, and reports `contract_satisfied: false`
  (`run.py:213`), attested in the rebuilt `verification.json` whose four
  artifact hashes all match my recomputation. As in rounds 3–5, this
  environment cannot execute Python, so executed-check attestations (py_compile,
  smoke, the known/unknown truncated-gzip fixtures, the finite-ratio admission
  fixture, the stale-marker refusal) plus static tracing are the basis.

## Verdict

The take-11 dual directive is implemented exactly and minimally: a two-line
contract amendment that authorizes excluding precisely the one verified
source-defective member and keeps every other unreadable or missing member
fail-loud; a run.py delta that reads every required gzip stream fully, routes
the preregistered defect to `schema_census.csv` and `exclusions.csv` with the
exact path, continues the map pass, surfaces the excluded count in
`summary.json`, and tightens stratum admission to finite rCBF and rCBV
identically in both passes — with Phase S, the split, all gates, thresholds,
and the analysis byte-unchanged. The amendment was correctly judged necessary,
so the standing approval is stale by construction and the runtime gate
enforces that; nothing can run until the human reviews the two-line contract
diff and binds a fresh approval to blob `2963f66b…`. Four new findings are
operational polish; none changes what the census measures.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Take-11 dual directive implemented exactly (single-member source_corrupt_member routing with fail-loud default, finite-ratio stratum admission in both passes, two-line contract amendment correctly judged necessary); approval stale by design pending fresh human binding to contract blob 2963f66b; four non-blocking operational findings."}
```
