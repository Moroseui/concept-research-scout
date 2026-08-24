# Probe code review — idea 023, round 3 (first review of the post-amendment code)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`8bd3156b1561569cfee01d40bf96d8a8a79e69c081d97fcd26f7da0dffb26eb2`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical to the
round-2 file), `probes/023/README.md` (SHA-256 `be45e902…`),
`probes/023/verification.json` (hashes match all three), against the AMENDED
`ideas/023/probe_contract.yaml` (git blob
`349af5ad0b3e8acfc6337d15f1860974d1183393` — diffed this round against the
on-disk file and against the blob in `ideas/023/HUMAN_APPROVED_PROBE`; all
three identical). Rounds 1–2 preserved at commits `f5cdd6a` and `bb696da`.

**Scope note.** The 2026-08-24 operator ruling authorized Phase S with the
round-2 code and required five resolutions before Phase C: blockers B1–B3,
the NaN-background finiteness ambiguity, and the NCCT-location correction.
The contract amendment (commit `64c9d7f`) froze the Phase-S gates (N=20,
M=100, CI width 0.15, simulation SHA-256 `59069fa9…`) and encoded the
finiteness and NCCT clause rulings; a fresh hash-bound approval now exists.
This review is the remaining code gate before Phase C runs on real data.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist; not a requirements-governed contract. Not applicable.

**External evidence:** none newly fetched. B1's fix is verified against the
official release filename quoted verbatim in the round-2 review
(`sub-strokecase0009_ses-0001_lesion-msk.nii.gz`, fetched 2026-08-24 from the
official repository tree).

---

## Disposition of the five operator-mandated resolutions

| Mandated item | Status in this code |
|---|---|
| B1 lesion filename | **Resolved** — suffix list is now `("_lesion-msk.nii.gz", "_lesion-msk.nii")` (`run.py:216`), matching the official spelling; prefix+suffix `rglob` tolerates the release quirk of a `ses-0001` filename stored under the follow-up session directory; lesion filenames are first resolved in pass two (`run.py:510`), preserving the label-blind freeze |
| B2 compute/memory/resume | **Resolved** — the mirrored 5×5×3 median is a vectorized, slab-bounded `sliding_window_view` + `nanmedian` (`run.py:416-434`), capped at ~12M window values (≈50–100 MB) per slab; each case is computed once, checkpointed atomically (`run.py:519-524`, `631`), and the outcome pass reuses the cached `rcbf`/`rcbv`/`region` (`run.py:702`) instead of recomputing; both passes resume per case (`run.py:613-618`, `689-700`); checkpoints are identity-bound to contract blob, archive SHA-256, split SHA-256, and `run.py` SHA-256 (`run.py:602-609`); no per-case full-volume state accumulates across the census loop |
| B3 secondary metrics | **Resolved** — median-d patient-bootstrap 95% CI from the same bootstrap index matrix (`run.py:727-737`, columns in `per_stratum_summary.csv`); label-blind native-support distribution (9 quantiles + count per stratum) in `support_summary.csv` plus dependency-free `native_support.svg` (`run.py:676-683`); identity-residual distribution in `identity_residual_summary.csv` plus SVG, both written **before** the exit-9 gate can fire (`run.py:658-673`) |
| Finiteness clause (amended `grid_gate`) | **Implemented as ruled** — nonfinite map voxels are excluded from the analyzed region (`run.py:440`, `461`) and counted per map in `exclusions.csv` (`run.py:465-468`); lesion finiteness is enforced only on analyzed voxels (`run.py:484-485`), with nonfinite background permitted; two precision notes below (F4) |
| NCCT clause | **Implemented as ruled** — the rawdata NCCT is a required input resolved by exact suffix (`run.py:214`, `325`; round 2 verified no derivative file shares it), the brain mask and mirror derive from it on the common canonical grid (`run.py:330`, `374-413`), and the README states the exact extraction set and that the NCCT exists only under `rawdata` — one glob typo in that README line (F3) |

## Round-2 non-blocking disposition

- **N1 (Phase S/C conjunction divergence): resolved.** Phase S now uses the
  direction-aware CI-exclusion rule (`run.py:159-160`), the same conjunction
  as Phase C (`run.py:732-739`). The frozen simulation hash was produced
  under the round-2 rule; for a percentile bootstrap of a mean the two rules
  cannot classify any replicate differently (opposite-side exclusion would
  require the point estimate to fall outside its own bootstrap interval), and
  the rule change consumes no randomness, so a rerun reproduces the frozen
  CSV; Phase C in any case verifies the stored artifact's hash before any
  data access (`run.py:300-310`, called at `run.py:571`).
- **N3 (evidence persistence on invalidating exits): resolved for the
  identity and mirror gates** — `mirror_qc.csv`, `schema_census.csv`,
  `exclusions.csv`, and the identity CSVs/SVG are all written before their
  exits (`run.py:647-651`, `666-673`). Residual: a unit-gate exit at case 1
  still leaves no CSVs, though per-case audit JSONs in `phase_c_cache/` and
  `run_log.txt` carry the evidence. Carried.
- **N4 (unit gate will likely stop a real run): carried unchanged**
  (`run.py:353-365`); the stop is the contract's mandated behavior.
- **N5 (extraction set undocumented): resolved** by the README section and
  the contract's corrected `required_inputs`; see F3 for the typo.
- **N6 (mirror narrowness): carried** — axis-aligned plane within ±5 voxels,
  no tilt model; the `zooms` parameter is accepted but unused (`run.py:374`),
  so the ≤1-voxel error bound remains in mixed index units across
  anisotropic axes. Frozen design; expect exit-7 as a plausible real-data
  stop.
- **N7 (archive digests read 99 GB twice): carried and amplified** — MD5 and
  SHA-256 remain separate full passes (`run.py:274`, `279`), and because
  provenance validation precedes checkpoint use, **every resume after a
  disconnect re-pays both passes (~30–60 min)** before any cached work is
  honored. A single pass updating both digests is still the cheap fix. The
  released case count is likewise still taken from the extracted directory
  without cross-check against `archive_manifest.csv`.
- **N8 (smoke overwrite): carried** — `--smoke` writes `summary.json` and
  friends into `--output-dir`; additionally, smoke now bypasses `gate()`
  entirely (`run.py:766`). Acceptable (synthetic only, labeled
  non-contractual, needed by the verify harness), but noted.
- **N9 (requirements pins): partially resolved** — `resolved_config.json`
  now echoes the three Phase-S-frozen thresholds in Phase C
  (`run.py:768-773`). `requirements.txt` keeps bounded ranges; freeze exact
  resolved versions for the real Phase C run and rely on `environment.txt`
  as the record of what actually installed.

## Blocking findings

None.

## Non-blocking findings (new this round)

**F1 — Quartile-cut population and measurement population differ by the
`mtt > 0` condition.** The label-blind stratum mask that estimates quartile
cuts, support, and the identity coordinate requires
`(cbf > 0) & (cbv > 0) & (mtt > 0)` (`run.py:476`); the outcome-pass mask
applies those cuts with only `rcbv > 0` (`run.py:489`). The `cbf`/`cbv`
positivity terms are implied by the stratum bounds and `rcbv > 0` given
valid denominators; `mtt > 0` is not — a voxel with MTT ≤ 0 inside the
analyzed region enters Q1/Q4 measurement but was excluded from cut
estimation and the support census. On vendor maps the set is likely near
empty (zero-fill usually hits all maps together, forcing `rcbv = 0` and
exclusion everywhere), and the discrepancy is label-blind either way, but a
preregistered instrument should apply its cuts to exactly the population
they were frozen on. Align the two masks at the next authorized touch and
record the choice.

**F2 — The outcome checkpoint rewrite is not atomic.** `write_csv`
rewrites `per_patient_checkpoint.csv` in place after each case
(`run.py:716`). A disconnect mid-rewrite that truncates at a row boundary
silently drops the trailing strata of the last recorded case on resume (a
mid-row truncation instead dies as exit 13 on a malformed row). The window
is microseconds per case, but the fix is free: reuse the tmp-file +
`os.replace` pattern already implemented in `atomic_npz` (`run.py:519-524`).

**F3 — README extraction glob for the NCCT matches nothing.** Line 29 of
`probes/023/README.md` reads `rawdata/**/_ncct.nii.gz` — missing the `*`
before `_ncct` (the lesion line above it has the correct form). Followed
literally, selective extraction yields zero NCCT files and Phase C exits 5
at the first case. The failure is cheap (re-extract from the local archive,
no new download) and the code itself resolves `*_ncct.nii.gz` correctly
(`run.py:214`), but this is the documentation line the amendment made
load-bearing; fix to `rawdata/**/*_ncct.nii.gz`.

**F4 — Finiteness clause: two precision gaps, both fail-safe.** (a) The
lesion finiteness check runs over the full cached region (`run.py:484-485`),
a superset of the per-stratum analyzed set, so a NaN at a region voxel
outside every rCBF stratum refuses the case — stricter than the amended
clause, in the safe direction. (b) Permitted nonfinite lesion values outside
the analysis region are excluded (`lesion > 0.5` is False for NaN) but not
**counted** anywhere, while the amended `grid_gate` says
"permitted, excluded, and counted"; `exclusions.csv` counts map nonfinites
only (`run.py:465-468`). Add a per-case nonfinite-lesion count in pass two.

**F5 — Concept-record lineage not pinned.** `validate_record_and_archive`
refuses a mutable concept record and verifies the Zenodo-supplied MD5
against the local archive (`run.py:263-276`), but never asserts
`conceptrecid == "16731717"`, the concept record the contract names. The
MD5 match to the on-disk archive bounds the risk; a one-line equality check
would close the provenance loop.

**F6 — Cache footprint and invalidation ergonomics.** `phase_c_cache/`
stores compressed full-volume `rcbf`/`rcbv`/`region` plus z/u vectors per
case — plausibly a few GB across 100 cases on the Drive output directory;
budget for it. The identity binding (`run.py:607-608`) correctly refuses
stale caches after any contract/code/archive/split change, but the exit-4
message does not tell the operator the remedy is to delete the cache
directory after an intentional change; say so.

**F7 — Edge-case exit mistaxonomy.** A stratum with zero supported voxels
across all 100 patients reaches `np.concatenate` of an empty list
(`run.py:660`) and dies as exit 13 (unexpected) rather than a clean exit
9/10. Practically unreachable in a census that passed the mirror gate;
recorded for completeness.

## Verified correct (spot-checked this round)

- **Approval gate:** blob-SHA1 binding to the marker, code/contract drift
  checks, and the Phase-C placeholder scan — grepped this round: zero
  `TO_BE_RECORDED` tokens remain in the amended contract, and every key
  `scalar()` parses (`idea_id`, `contract_version`, the three caps, the
  three frozen thresholds, `simulation_output_sha256`) occurs exactly once,
  so the single-occurrence parser cannot misread the contract.
- **Phase-S hash chain:** Phase C requires `--phase-s-dir`, recomputes the
  simulation CSV's SHA-256, and compares it to the amended contract value
  before touching the record, archive, or images (`run.py:571`).
- **Phase S simulation:** unchanged in contract terms — 60-candidate ×
  9-scenario grid matching the frozen constants, Beta/Binomial generator,
  2000/2000 replicates, 2000-resample bootstrap, seed 20260824,
  every-cell eligibility, lexicographic (smallest N, smallest M, largest
  width) selection, `PHASE_S_FAILED` summary persisted before exit 10.
- **Split and freeze-before-look:** SHA-256(`idea-023-v1|` + case_id), 100
  lowest hashes to census, disjointness asserted, manifest + SHA-256 frozen
  before any image opens; quartile cuts, mirror QC, unit gate, and identity
  gate all complete in the label-blind pass; reserved patients never
  opened; `test`-path refusal on data, archive, and record paths.
- **Analysis discipline:** equal patient weight, patient-only bootstrap
  (`default_rng(20260824)`, single stream), the exact three-stratum
  conjunction with direction-consistent CI exclusion, support shortfall
  exits 10 as invalidating (never counted as a negative), CI-width failure
  correctly classified as `negative_pattern` per the contract, no pooled or
  fallback analysis, one variant, one seed, zero GPU.
- **Slab median equivalence:** the mirrored-window arithmetic
  (`mirrored[i±2, j±2, k±1] = source[reflect(i)∓2, …]`) reproduces the
  frozen reflected 5×5×3 neighborhood exactly, deficit/vessel/non-brain
  voxels are NaN-masked before the median, and all-NaN windows propagate to
  counted denominator exclusions; the builder's seeded fixture check in
  `verification.json` agrees.
- **Required outputs:** all 16 contract outputs are written across the two
  phases, plus the two SVG plots the README documents.
- **Claim discipline:** statuses are the contract's
  `POSITIVE_PATTERN`/`NEGATIVE_PATTERN`; closing interpretations forbid
  physiological and model-use language; smoke is labeled non-contractual.
- **Harness lessons:** full tracebacks precede exit 13; the only rename is
  same-directory `os.replace`; JSON writers reject NaN (`allow_nan=False`);
  no network access anywhere.

## Verdict

All five operator-mandated resolutions — the lesion filename, the Colab
compute/memory/resume plan, the three preregistered secondary outputs, the
analyzed-voxel finiteness scoping, and the rawdata-NCCT requirement with a
documented extraction set — are correctly implemented, and the frozen
Phase-S thresholds are read from the amended contract rather than
hardcoded. The remaining findings are polish items that do not change what
the census measures, do not create silent wrong-number paths under
realistic conditions, and are individually cheap to absorb at the next
authorized touch (F3, the README glob typo, is worth fixing before the
archive is extracted). Phase C is faithful to the amended contract and may
run under the standing approval.

```json
{"verdict": "APPROVE", "blocking": [], "note": "All five mandated resolutions (B1-B3, finiteness scoping, rawdata NCCT) verified implemented; seven non-blocking polish findings recorded, the only user-facing one being a one-character README extraction-glob typo (F3) worth fixing before extraction."}
```
