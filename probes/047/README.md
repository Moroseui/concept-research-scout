# Probe 047 — keystone-ten support arithmetic and clinical profile (contract v2, draft)

`ideas/047/probe_contract.yaml` (contract_version 2, not yet approved)
specifies one CPU-only, two-phase pipeline for idea 047. No code exists
yet; this README records the plan the contract binds. Probe code may be
written only after probe review and explicit human approval of the
contract blob.

v2 supersedes the v1 draft per the feasibility REVISE verdict
(`ideas/047/feasibility.md`): the support variable `B_i` already exists
as a claim-bearing output of the ratified take-13 bundle, so the v1 map
restaging (~3 GB, 495 image members), the region recomputation, and the
297-row reproducibility gate are all retired. The v1 draft is preserved
at commit `63459ec`.

## What the probe tests first (the riskiest assumption)

Before any science is emitted, Phase A must pass a provenance-and-join
gate on the cached support extract, entirely from pinned in-repo bytes:

- `probes/023/results/results_v2/exclusions.csv` (sha256 `58e9f8ab…`),
  filtered to `record_type == analyzed_case`, must yield exactly 99
  unique case ids **set-equal** to the 99 ids of the frozen contribution
  table (`probes/046/results/results_v3/per_case_contributions.csv`,
  sha256 `aba52512…`), each with a finite positive integer
  `eroded_region_voxels` — this is `B_i`;
- the only non-analyzed rows must be the two documented bookkeeping rows
  (`sub-stroke0142` excluded_archive_lesion, `sub-stroke0043`
  excluded_case);
- `probes/023/run.py` must byte-match frozen blob
  `0e9a40b453b6d4b653841d6ea70f2e4b75cce9be`, whose
  `coordinate_arrays()` (lines 486–523) writes `eroded_region_voxels`
  as the eligible region after Tmax>6.0 thresholding, six-neighbor
  erosion, border + two-voxel array-midline exclusion, per-patient p98
  CBV vessel exclusion, and finiteness/positivity filtering. The code
  is evidence and is **never executed** under this contract.

All of this was verified by hand at drafting (2026-09-02; hashes
reproduce, join exact, `B_i` range 1401–617540). A gate failure stops
the run as `SUPPORT_PROVENANCE_FAILURE` with the gate record as the
deliverable; no substitute support source may be consulted.

## Phase structure (one contract, right-sizing ruling 2026-09-01)

- **Phase A (phenotype-blind, table-and-dictionary-only; no archive
  access):** identity gates → provenance-and-join gate → census
  cross-checks → the frozen finite-population support clause —
  `sum_head |c_i| / sum_all |c_i|` beside `sum_head B_i / sum_all B_i`,
  rank-discrepancy display, descriptive Spearman rho, and the 79.29%
  signed share only as labeled reversal accounting — then a
  dictionary-only inventory of `clinical_data-description.xlsx`
  (12,149 bytes, md5 pinned `c8d806a0…`) with a machine-derived
  proposed variable freeze. Terminal:
  `PHASE_A_COMPLETE_REQUIRES_AMENDMENT` (or
  `PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED` if the dictionary cannot
  support the minimum variable set). Wall-clock: minutes.
- **Amendment + fresh approval:** binds the frozen clinical variable
  list from the dictionary inventory (24-hour NIHSS is the
  lineage-preserving field; admission NIHSS is contextual; center
  mandatory-if-documented) and swaps `required_outputs` to the Phase-B
  interface. Only this fresh approval authorizes staging or reading any
  phenotype byte.
- **Phase B (clinical):** one selective staging event of exactly the
  **198** phenotype members (99 × `demographic_baseline.csv` +
  99 × `outcome.csv`) from the held md5-verified `train.7z` (Zenodo
  record 16813698), size/CRC-checked against the frozen archive
  manifest, then one aggregate 10-versus-89 estimation table under D4:
  joint support display, per-group missingness, small-cell suppression,
  and two exploratory-labeled uncertainty displays per contrast
  (deterministic leave-one-head-case-out ranges, plus a relabeling
  range explicitly labeled a hypothetical exchangeability reference,
  seed 20260902). Terminal: `STUDY_COMPLETE`.

Blindness is stronger than in v1: no phenotype byte is even staged to
disk until the Phase-B approval exists. **No perfusion map, NCCT, or
lesion-mask member is staged or read in either phase**, and the 49
reserved cases and `sub-stroke0043` are never touched.

## What no outcome authorizes

Both terminal statuses are descriptive. The probe defines no
proportionality verdict, no keystone label, no clinically-silent or
clinically-marked reading, no per-patient claim, no model-use or causal
claim, and no generalization beyond the realized 99 cases. The signed
79.29% share may never be compared against the support share as
contribution per unit support.

## Expected sequence

probe review → human approval of contract v2 (three open questions:
cached-support substitution for the unblock ruling's literal
recomputation branch; uncertainty currency; one-contract structure) →
probe-build (`run.py` here) → Phase A → record-result → mechanical
amendment + fresh approval → Phase B → record-result → interpret →
ratify. An `ideas/047/registry.yaml` two-node DAG (phase_a → phase_b
with the declared artifact edge) is authored at approval per the
registry-per-probe rule.
