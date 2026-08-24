# Probe code review — idea 023, round 1

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`bd42b9ebc998f89c8b7dea6dbe8ace44d74e2aea1ac61389559de8a333dfa006`),
`probes/023/requirements.txt`, `probes/023/README.md`,
`probes/023/verification.json`, against `ideas/023/probe_contract.yaml`
(git blob `4a46713d1b81874c88a2e347aace6773e68904e2` — verified identical to
the blob named in `ideas/023/HUMAN_APPROVED_PROBE`).

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist; this is not a requirements-governed contract. Not applicable.

**Scope note.** The standing approval authorizes Phase S (synthetic-only). The
code's Phase C path is mechanically locked behind the placeholder check and a
fresh hash-bound approval (verified: `verification.json` records exit 2 on the
pre-amendment Phase C attempt). However, the committed `run.py` *contains* the
Phase C implementation, and this round is the gate at which it must match the
preregistration. The blocking findings below therefore include Phase C: this
file must not become the reference implementation that enters the
amendment/approval cycle in its current state.

---

## Blocking findings

**B1 — Phase C file discovery is guaranteed to fail on the documented release
schema (contract fidelity / practicalities).** `run.py:237` resolves the NCCT
volume with `find_one(root, [case_id, "ncct"])`, but every derivative filename
in the release contains the substring `ncct` via `space-ncct`
(`sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz`, etc. — the exact
filenames quoted in `ideas/023/keystone_screen.md`). `find_one`
(`run.py:198-202`) requires exactly one match; at least the four perfusion maps
match, so the call exits 5 on the very first census case, in the label-blind
pass. Phase C as written cannot execute against the schema the contract
targets. Related fragility in the same function: `run.py:234-235` picks
`roots[0]` among possibly-multiple directories named `sub-strokecaseNNNN`
(raw subject dir vs `derivatives/` subject dir) in filesystem iteration order —
which directory wins is nondeterministic.

**B2 — The contract's `brain_and_mirror_gate` is not implemented, and a code
comment claims it is (contract fidelity / silent failure).** The contract
requires: brain mask and midsagittal reflection derived from the registered
NCCT by one frozen automatic method; median left-right NCCT registration error
≤ one in-plane voxel; usable mirrored support for ≥ 90% of brain-mask voxels in
≥ 90 census patients — all before outcomes are read — plus `mirror_qc.csv`.
The code instead uses a bare array-axis-0 flip as the mirror
(`run.py:255-256`), takes the array midpoint as the midline (`run.py:270-271`),
derives no brain mask, computes no registration-error statistic, writes no
`mirror_qc.csv`, and loads the NCCT volume without ever using it. The comment
at `run.py:253-254` ("The one-voxel NCCT registration-error gate is reported
conservatively via normalized MAE") describes code that does not exist. The
contract's invalidating class "Mirror failure" is undetectable; exit 7 is
unreachable.

**B3 — `relative_measures` deviates from the frozen preprocessing rule
(contract fidelity).** The contract freezes: divide CBF and CBV by the median
of the reflected 5×5×3-voxel contralateral neighborhood *after excluding
deficit and vessel voxels*, with nonpositive/nonfinite denominators excluded
*and counted*. `run.py:257-259` divides by the single mirrored voxel value —
no neighborhood median, no exclusion of deficit/vessel voxels from the mirror
reference, and no exclusion counting anywhere (see B7, `exclusions.csv`).
This is an unregistered variant of the frozen measurement.

**B4 — Central-volume identity gate: wrong centering and wrong ordering
(contract fidelity / analysis deviation).** The contract specifies subtracting
the *census-wide* median u and states the 0.10 gate "invalidates this
coordinate and stops before outcome modeling." The code (a) centers residuals
per stratum (`run.py:374`), which absorbs stratum-level offsets the
census-wide centering would expose, and (b) evaluates the gate only after
lesion masks have been opened, per-patient contrasts computed, and bootstrap
summaries built (`run.py:352-376`), with `per_patient.csv` (label-derived)
already on disk. The residual is computable from maps alone and belongs in the
label-blind pass.

**B5 — Unit gate missing (contract fidelity).** The contract: "The CBV cap is
valid only if Phase-C unit inspection confirms mL/100 g; otherwise stop for
contract amendment before outcomes are read" (invalidating class "Unit
failure", exit 8). The code applies `cbv <= 8.0` (`run.py:261`) with no unit
inspection of any kind; exit 8 is declared in the docstring but unreachable.

**B6 — Provenance recording and verification not implemented (contract
fidelity / silent failure).** The contract's dataset section requires, before
analysis: selection of one immutable Zenodo child record and recording of its
record id, publication date, Zenodo-supplied `train.7z` checksum, downloaded
SHA-256, case count, and archive member manifest. The code computes the
archive SHA-256 only at the end (`run.py:385`), never compares it to a
Zenodo-supplied checksum, accepts any local `--record-json` without validating
it is the pinned immutable record (only `record.get("id")` is echoed), writes
no `archive_manifest.csv` or `schema_census.csv`, and never records
`split_manifest.csv`'s own SHA-256 (the split policy says "Freeze
split_manifest.csv and its SHA-256"). Exit 4 (provenance) is unreachable: a
"Provenance failure" cannot be detected by this code.

**B7 — Required outputs missing (contract fidelity).** Four files in
`required_outputs` are never written by any phase: `archive_manifest.csv`,
`schema_census.csv`, `mirror_qc.csv`, `exclusions.csv`. The contract's
"Output failure" class makes missing required outputs invalidating; the code
cannot produce a valid Phase C run by its own contract.

**B8 — Grid gate does not implement the frozen resampling rule (contract
fidelity).** The contract permits resolving header mismatches "only by the
preregistered interpolation rule: linear for maps, nearest-neighbor for
labels; record every resampling." The code exits 6 on any grid difference
(`run.py:242-244`). The direction is fail-safe (refuse rather than silently
resample), but it leaves the preregistered rule unimplemented and would
mislabel contract-resolvable data as an invalidating grid failure.

**B9 — Phase C entry condition incompletely enforced (contract fidelity).**
`phase_C_real_census.entry_condition` requires that "the simulation output
hash verifies." `gate()` (`run.py:97-120`) checks placeholder absence and the
hash-bound approval, but nothing ever verifies the amended contract's
`simulation_output_sha256` against the actual Phase-S
`simulation_operating_characteristics.csv` (e.g., via a required
`--phase-s-dir` argument compared at Phase C startup).

## Non-blocking findings

**N1 — CI direction.** Both phases count a CI as "excluding zero" via
`lo > 0 or hi < 0` (`run.py:151`, `run.py:368`); the contract's pass rule says
"exclude zero *in that common direction*." With a percentile bootstrap of a
mean the divergence is practically unreachable (the interval brackets the
point estimate), but the literal rule is one comparison away.

**N2 — Erosion order.** The code intersects Tmax > 6 with the vessel cap and
valid-denominator masks *before* the one-voxel erosion (`run.py:261-268`);
the contract reads erode-the-deficit-mask-then-exclude. The coded variant is
strictly stricter (voxels adjacent to exclusions are also eroded away) but is
not the registered rule; fold the fix into B3.

**N3 — Case count.** 149 vs 150 is accepted (`run.py:209-210`) but the
discovered count is not recorded in `summary.json`, and the contract's
"resolved by archive census rather than assumed" instruction has no recorded
resolution output.

**N4 — Secondary metric gap.** The "label-blind native-support plot of z by
rCBF stratum" is only partially covered by `support_summary.csv` quartiles and
counts; no distribution output exists.

**N5 — Phase S runtime.** The full grid is ~2.16 M simulated conjunctions,
each with a 2,000-replicate bootstrap — on the order of one to a few CPU-hours
in Colab, single-threaded, with no checkpointing; a disconnect loses the run.
Deterministic seeding makes reruns cheap, but consider vectorizing across
replicates or emitting per-scenario progress.

**N6 — Memory.** Identity residuals accumulate as a Python list of
`(stratum, float)` tuples over all deficit voxels of 100 patients
(`run.py:301`) — plausibly 10⁶–10⁷ entries (~1 GB). Use arrays.

**N7 — Smoke overwrite.** `--smoke` writes `summary.json` and friends into
`--output-dir` and can silently overwrite a real Phase-S result if pointed at
the same directory.

**N8 — Requirements pins.** Bounded ranges rather than exact pins (the
frozen numpy 1.26.4 had no Python 3.13 wheel; honestly recorded in
`verification.json`, and every run records resolved versions in
`provenance.json`). Acceptable now; freeze exact resolved versions for the
eventual Phase C run.

## Verified correct (so they are not re-reviewed next round)

- **Approval gate mechanics:** git-blob-SHA1 binding of the marker to the
  contract; drift checks on frozen literals; refusal of Phase C while any
  `TO_BE_RECORDED_AFTER_PHASE_S` placeholder remains (`run.py:117-118`);
  amendment stales the approval by construction.
- **Phase S implements the contract's simulation exactly:** Beta(p0(1/ρ−1),
  (1−p0)(1/ρ−1)) latent risks, Binomial(M,·)/M quartile risks, δ ∈ {0, 0.05},
  three strata, 2000/2000 replicates, 2000-resample patient bootstrap, seed
  20260824; eligibility requires FPR ≤ 0.05 in *every* null cell and power
  ≥ 0.80 in *every* alternative cell; lexicographic selection (smallest N,
  smallest M, largest width) at `run.py:185`; no-eligible-candidate exits 10
  without selecting, as the contract requires.
- **Split policy:** SHA-256(`idea-023-v1|` + case_id), 100 lowest hashes to
  census, disjointness asserted, manifest written before any label access;
  reserved cases never opened; a `test`-path refusal guard on top.
- **Freeze-before-look:** two-pass Phase C; quartile cut points estimated
  from a maps-only pass (`load_label=False`); lesion filenames are not even
  resolved until pass two.
- **Analysis discipline:** equal-patient weighting, patient-only bootstrap,
  the exact three-stratum conjunction, no pooled or fallback analysis;
  support shortfalls exit 10 as invalidating, never as a negative.
- **Claim discipline:** summary statuses use the contract's
  `positive_pattern`/`negative_pattern` names; smoke output is labeled
  non-contractual; the Phase S interpretation instructs stop-amend-reapprove;
  no physiological or model-use language anywhere in the outputs.
- **Budget:** one variant, one seed, zero GPU minutes; no network access.
- **Readability:** narrated docstring, phase banners, threshold provenance
  comments, progress printing, plain-English closing interpretation. The one
  false comment is covered by B2.

## Verdict

Phase S is faithful and could run today. Phase C, as committed, cannot run at
all on the real schema (B1) and omits or deviates from five frozen contract
elements (B2–B6), leaves four required outputs unwritten (B7), and skips two
entry/resolution rules (B8–B9). Since the round-1 code is the artifact the
amendment cycle will build on, these must be repaired before approval.

```json
{"verdict": "REVISE", "blocking": ["B1: Phase C NCCT lookup matches every space-ncct filename, so find_one exits 5 on the first census case; case-root selection is also order-dependent (run.py:234-237)", "B2: brain_and_mirror_gate (brain mask, NCCT midsagittal method, <=1-voxel registration-error gate, >=90%/>=90-patient mirrored support, mirror_qc.csv) is unimplemented; comment at run.py:253-254 claims a gate that does not exist", "B3: relative_measures uses single mirrored voxel instead of the frozen reflected 5x5x3 neighborhood median with deficit/vessel exclusion and counted exclusions (run.py:257-259)", "B4: identity-residual gate centers per stratum instead of census-wide and runs after outcome access instead of before outcome modeling (run.py:300,352-376)", "B5: CBV-cap unit inspection (mL/100 g) is absent; exit 8 unreachable (run.py:261)", "B6: provenance rules unimplemented: no Zenodo-checksum comparison, no immutable-record validation, no pre-analysis archive manifest, split-manifest SHA-256 unrecorded (run.py:312-320,385)", "B7: required outputs archive_manifest.csv, schema_census.csv, mirror_qc.csv, exclusions.csv are never written", "B8: frozen linear/nearest resampling rule not implemented; any header mismatch exits 6 (run.py:242-244)", "B9: Phase C entry condition 'simulation output hash verifies' is never checked against the Phase-S CSV (run.py:97-120)"], "note": "Phase S is contract-faithful and runnable; Phase C is dead on arrival against the release schema and omits five frozen gates plus four required outputs — revise before the amendment cycle builds on this code."}
```
