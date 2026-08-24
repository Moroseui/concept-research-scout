# Probe code review — idea 023, round 2

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`0faf04241ddb2c8064635105d1581880d33d05f3981c0f33deec9f1d4fc38b24`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, matches
`verification.json`), `probes/023/README.md`, `probes/023/verification.json`,
against `ideas/023/probe_contract.yaml` (git blob
`4a46713d1b81874c88a2e347aace6773e68904e2` — verified identical to the blob in
`ideas/023/HUMAN_APPROVED_PROBE`). Round-1 review preserved at commit
`f5cdd6a`.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist; not a requirements-governed contract. Not applicable.

**Scope note.** Unchanged from round 1: the standing approval covers Phase S
only, and the code's Phase C path is mechanically locked (placeholder scan +
hash-bound approval; placeholders confirmed present only in the four
`outputs_to_amend` values, so the full-file scan clears correctly after
amendment). Phase C is still reviewed here because this file is the reference
implementation entering the amendment/approval cycle.

**External evidence fetched this round:** the official repository's
data-structure tree (github.com/ezequieldlrosa/isles24, README, fetched
2026-08-24) — the same source the keystone screen relied on — quoted verbatim
where cited below.

---

## Round-1 blocker disposition

| Round-1 finding | Status in this code |
|---|---|
| B1 NCCT substring match / nondeterministic case root | **Fixed** — exact-suffix resolution (`run.py:198-213`), no case-root selection; but the same defect class recurs on the lesion mask (new B1) |
| B2 mirror gate unimplemented | **Fixed** — `mirror_qc` (`run.py:366-405`): NCCT-derived brain mask, plane search, per-patient registration error and usable fraction, `mirror_qc.csv`, ≥90-patient gate (`run.py:533-540`), exit 7 reachable |
| B3 single-voxel mirror reference | **Fixed** — reflected 5×5×3 `nanmedian` with deficit/vessel/brain exclusion (`run.py:408-415`, `423-426`) and counted exclusions (`run.py:442-444`); runtime consequence in new B2 |
| B4 identity gate centering/ordering | **Fixed** — census-wide median, per-stratum MAD, gated in the label-blind pass before any lesion filename is resolved (`run.py:542-552`) |
| B5 unit gate missing | **Fixed** — `confirm_cbv_units` (`run.py:345-357`); exit 8 reachable, checked in the label-blind pass |
| B6 provenance unimplemented | **Fixed** — immutable-record validation (concept-record refusal), Zenodo-MD5 comparison, archive SHA-256, member manifest before analysis, split-manifest SHA-256 recorded (`run.py:248-287`, `492-510`) |
| B7 required outputs missing | **Fixed** — all 16 `required_outputs` are written across the two phases |
| B8 resampling rule unimplemented | **Fixed** — linear for maps, nearest for labels, every resampling recorded in `schema_census.csv` (`run.py:323-341`) |
| B9 Phase-S hash never verified | **Fixed** — `verify_phase_s_hash` compares the amended `simulation_output_sha256` to the actual Phase-S CSV before any data access (`run.py:290-300`, called first at `run.py:490`) |

Round-1 non-blocking items: N2 (erosion order) fixed (`run.py:430-441`,
erode-then-exclude); N3 (case count) fixed (`released_case_count` in
provenance and summary); N6 partially fixed (voxel accumulators now
per-stratum arrays, but see new B2); N1, N4, N5, N7, N8 unaddressed — N4 is
escalated into new B3; the rest are carried below.

## Blocking findings

**B1 — Lesion-mask discovery fails on the documented release schema; Phase C
dies at the first outcome-pass case (contract fidelity / practicalities).**
The official repository's data tree names the ground truth
`sub-strokecase0009_ses-0001_lesion-msk.nii.gz` — the suffix is
`_lesion-msk.nii.gz`, with a hyphen before `msk`. The code's lesion suffix
list (`run.py:206`) is `("_msk.nii.gz", "_msk.nii", "_lesion.nii.gz",
"_lesion.nii")`; none matches (`_msk.nii.gz` requires an underscore before
`msk`, `_lesion.nii.gz` requires `lesion` to be terminal). `find_one` finds
zero files and exits 5 at `run.py:575` on the first case of the outcome pass —
after the entire multi-hour label-blind pass has completed. This is the second
consecutive round in which Phase C cannot execute against the schema quoted in
this repository's own keystone documents; the fix must match the verbatim
release name (and note the release quirk that the mask file sits in the
follow-up session directory while its filename carries `ses-0001` — the
prefix+suffix match is robust to that, the suffix is the only defect).

**B2 — The Phase C compute/memory envelope is not runnable in Colab
(practicalities).** Three compounding problems. (a) `neighborhood_median`
(`run.py:415`) uses `scipy.ndimage.generic_filter` with `np.nanmedian`, which
invokes a Python callback per output voxel (~15–35 µs each). It runs on the
full volume, twice per case (CBF and CBV), and — because pass two calls
`coordinate_arrays` again (`run.py:459`) instead of reusing pass-one products —
twice more per case in the outcome pass. At plausible NCCT-grid sizes this is
4 × 10⁷–10⁸ callback invocations per case: roughly 20–30 CPU-hours for the
census at thick-slice dimensions and multiple days at thin-slice dimensions,
single-threaded. (b) There is no checkpoint/resume: a Colab disconnect at
case 90 of the label-blind pass loses everything. (c) `mirrors` (`run.py:527`)
retains a full-volume boolean brain mask for all 100 census patients
simultaneously — 1–8 GB depending on grid size, on top of per-case working
arrays, risking OOM on a standard Colab VM. Required repairs: a vectorized
mirrored-neighborhood median (or equivalent rank-filter formulation), reuse or
disk-cache of pass-one per-case products so nothing is computed twice, per-case
checkpointing so an interrupted census resumes, and per-case mirror state
reduced to what pass two needs (plane and reflection index, with the brain
mask recomputed or cached to disk).

**B3 — Preregistered secondary metrics are not computed (contract fidelity).**
The contract's `secondary_metrics` freeze three outputs this code never
produces: (a) "Median patient-level d and **its patient-bootstrap 95% CI** per
stratum" — `per_stratum_summary.csv` carries only the `median_d` point
estimate (`run.py:592-594`), no interval; (b) "a label-blind native-support
plot of z by rCBF stratum" — `support_summary.csv` (`run.py:562-568`) emits
only the two quartile cut points and a voxel count, no distribution (round-1
N4, unaddressed, now blocking); (c) "the identity-residual distribution" —
`identity_residual_summary.csv` (`run.py:553-556`) emits only the per-stratum
median absolute residual. The contract's Output-failure class makes missing
required records invalidating; a Phase C run of this code could not produce
the preregistered artifact set even if it executed.

## Non-blocking findings

**N1 (carried) — Phase S / Phase C conjunction inconsistency.** Phase C now
correctly requires CI exclusion in the common direction (`run.py:591`), but
Phase S still counts any exclusion (`run.py:151`), while the contract says
Phase S replicates are analyzed "with the exact three-stratum conjunction …
specified for Phase C". The divergence is practically unreachable for a
percentile bootstrap of a mean, but the two implementations should be one
shared function.

**N2 — Whole-volume finiteness gate may refuse real maps.** `run.py:334-335`
exits 6 if any voxel anywhere is nonfinite, implementing the `grid_gate`
literally ("require finite … arrays"), while the invalidating-failure class
says "nonfinite values remain **in analyzed voxels**". Vendor perfusion maps
plausibly carry NaN background outside the brain; if so, every case exits 6.
Fail-safe in direction, but the operator should decide at amendment time which
reading the contract intends, before a 99 GB download is spent discovering it.

**N3 — Invalidating exits do not persist their evidence.** The identity gate
fails (`run.py:552`) before `identity_residual_summary.csv` is written, and a
unit-gate failure at case 1 leaves no `schema_census.csv`/`mirror_qc.csv`
rows on disk (written only after the loop, `run.py:536-538`). Only
`run_log.txt` records the values. Write the diagnostic CSVs before raising.

**N4 — Unit gate will likely stop a real run.** `confirm_cbv_units` accepts
only an explicit "mL/100g" in a JSON sidecar or the NIfTI `descrip` field.
If the release documents units nowhere machine-readable, Phase C stops at
exit 8 — which is the contract's mandated behavior, but plan for the
amendment that follows rather than treating it as unexpected.

**N5 — Extraction requirements undocumented; feasibility memo misleads.** The
code needs the rawdata NCCT (`_ncct.nii.gz` resolves uniquely there; verified
no derivative file ends in `_ncct.nii.gz`), but `probes/023/README.md` never
says so, and `ideas/023/feasibility.md` §2 claims derivatives contain a
"registered NCCT" — per the official tree they do not. A user following the
memo's derivatives-only extraction gets exit 5 with zero NCCT matches. State
the exact extraction set in the README.

**N6 — Mirror method narrowness.** The midsagittal search is an axis-aligned
plane within ±5 voxels of the volume center (`run.py:377-378`) with no tilt
model; off-center or rotated heads — common in acute stroke CT — fail toward
exit 7. Fail-safe, and the ≥90/100 gate is the contract's own design, but
expect this as a plausible real-data stop. Also, the "one in-plane voxel"
error bound is operationalized as an EDT distance in mixed voxel units across
anisotropic axes; acceptable as a frozen method, worth stating in the run log.

**N7 — Archive digests read 99 GB twice.** `validate_record_and_archive`
computes MD5 and SHA-256 in separate full passes (`run.py:264`, `269`); one
pass updating both digests halves a ~30–60 min step. The released case count
is also taken from the extracted directory rather than cross-checked against
`archive_manifest.csv`.

**N8 (carried) — Smoke overwrite.** `--smoke` writes `summary.json` and
friends into `--output-dir` and can clobber a real Phase-S result.

**N9 (carried) — Requirements pins.** Bounded ranges remain acceptable for
Phase S; freeze exact resolved versions before the eventual Phase C run.
`resolved_config.json` should also echo the three Phase-S-frozen thresholds
when Phase C runs, so the run is auditable from its own output directory.

## Verified correct (not re-reviewed next round)

- **Approval gate mechanics** unchanged and re-verified: blob-SHA1 binding,
  frozen-literal drift checks, placeholder refusal for Phase C
  (`run.py:97-120`); amendment stales the approval by construction.
- **Phase S simulation** re-verified against the contract line by line:
  Beta/Binomial generator, δ ∈ {0, 0.05}, 2000/2000 replicates, 2000-resample
  bootstrap, seed 20260824, every-cell eligibility, lexicographic selection
  (`run.py:185`), no-eligible-candidate exits 10 without selecting,
  `PHASE_S_FAILED` summary persisted before the exit.
- **Split policy:** SHA-256(`idea-023-v1|` + case_id), 100 lowest to census,
  disjointness asserted, `split_manifest.csv` + SHA-256 frozen before label
  access; reserved cases never opened; `test`-path refusal on data, archive,
  and record paths.
- **Freeze-before-look:** two-pass Phase C; quartile cuts, mirror QC, identity
  gate, and unit gate all complete in the label-blind pass; lesion filenames
  first resolved in pass two.
- **Analysis discipline:** equal-patient weighting, patient-only bootstrap,
  the exact conjunction including the direction-consistent exclusion count,
  support shortfalls exit 10 as invalidating, no pooled or fallback analysis,
  one variant, one seed, zero GPU.
- **Claim discipline:** statuses use `positive_pattern`/`negative_pattern`
  names; interpretations forbid physiological and model-use language; smoke
  labeled non-contractual.
- **Harness lessons applied:** unexpected failures print a full traceback
  before exit 13; no bare cross-device renames; no network access.
- **Readability:** narrated docstring, phase banners, threshold provenance
  comments, per-case progress, plain-English closing interpretation.

## Verdict

Round 2 is a large, genuine improvement: all nine round-1 blockers were
addressed as specified, and Phase S remains contract-faithful and runnable
today. But Phase C — the artifact the amendment cycle will freeze — still
cannot complete a real run: it dies on the release's actual lesion filename
(B1), its innermost loop and memory plan do not fit the stated Colab envelope
and cannot survive a disconnect (B2), and three preregistered secondary
outputs are never produced (B3).

```json
{"verdict": "REVISE", "blocking": ["B1: lesion suffix list (run.py:206) matches nothing in the release schema — official tree names the mask sub-strokecase0009_ses-0001_lesion-msk.nii.gz (suffix _lesion-msk.nii.gz); find_one exits 5 on the first outcome-pass case", "B2: Phase C is not runnable in Colab — generic_filter/nanmedian mirrored median (run.py:415) executed four times per case across two passes, no checkpoint/resume, and 100 resident full-volume brain masks (run.py:527) risk OOM; vectorize, cache pass-one products, checkpoint per case, bound memory", "B3: preregistered secondary metrics never computed — median-d patient-bootstrap 95% CI (run.py:592-594), label-blind native-support distribution of z (run.py:562-568), identity-residual distribution (run.py:553-556)"], "note": "All nine round-1 blockers were properly fixed and Phase S can run today, but Phase C still dies on the real lesion filename, exceeds the Colab envelope with no resume path, and omits three frozen secondary outputs — revise before amendment."}
```
