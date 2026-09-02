# Probe 047 — keystone-ten support arithmetic and clinical profile (contract v2)

The human-approved `ideas/047/probe_contract.yaml` (contract_version 2,
blob `b4887c05a21bfe870589b5d9982066943df679d5`) governs this probe.
`run.py` implements **Phase A only** — the phenotype-blind support
clause plus the dictionary inventory and machine-proposed clinical
variable freeze. Phase B is locked behind the mechanical amendment and
a fresh human approval; this code refuses an amended contract by
construction (the authority gate requires the pre-amendment
`frozen_variable_list` sentinel, and the amendment stales the approval
blob).

## Running Phase A

One command into a new, empty output directory. The probe performs **no
network access**: `--dictionary-file` is a required pre-staged input — a
held copy of `clinical_data-description.xlsx` from immutable Zenodo
record 16813698 (12,149 bytes, md5 `c8d806a0…`), verified against those
pins before any cell is read. The probe refuses to run without it:

```bash
python probes/047/run.py --output-dir /path/to/probe-047-phase-a --dictionary-file /path/to/clinical_data-description.xlsx
```

Synthetic harness check (no real inputs, no network, never a gate):

```bash
python probes/047/run.py --smoke --output-dir /tmp/probe-047-smoke
```

Exit codes: 0 valid completion (`PHASE_A_COMPLETE_REQUIRES_AMENDMENT`,
`PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED`, or `SMOKE_ONLY`); 2
authority/CLI; 3 input identity; 4 pre-registered support-provenance
stop; 5 census cross-check (invalidating transcription); 6
scope/blindness; 7 output/determinism; 8 wall time; 12 unexpected fault.

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
  `coordinate_arrays()` (lines 486–523, recorded verbatim in
  `resolved_config.json`) writes `eroded_region_voxels` as the eligible
  region after Tmax>6.0 thresholding, six-neighbor erosion, border +
  two-voxel array-midline exclusion, per-patient p98 CBV vessel
  exclusion, and finiteness/positivity filtering. The code is evidence
  and is **never executed** under this contract.

All of this was re-verified by hand at probe-build (2026-09-02; hashes
reproduce, join exact 99/99, `B_i` range 1401–617540). A gate failure
stops the run as `SUPPORT_PROVENANCE_FAILURE` (exit 4) with the gate
record as the deliverable — a pre-registered decision-grade stop, not a
negative and not invalidating; no substitute support source may be
consulted.

## Phase-A outputs

The contract interface — `resolved_config.json`, `input_manifest.csv`,
`provenance_gate.json`, `per_case_support.csv`, `support_shares.json`,
`rank_discrepancy.csv`, `dictionary_inventory.csv`,
`proposed_variable_freeze.json`, `summary.json`, `environment.txt`,
`run_log.txt` — plus the case-identified split manifest (the analyzed
case ids from the phenotype-blind exclusions table, hashed **before**
the outcome-derived contribution table is opened; the support gate then
requires exact id equality against it), start/end determinism manifests
covering every input including the pre-staged dictionary (finalized on
the decision-grade stop path too), the bookkeeping exclusions log, and
the staged dictionary copy. The support clause is
exact finite-population arithmetic: `sum_head |c_i| / sum_all |c_i|`
beside `sum_head B_i / sum_all B_i` (the only two numbers the
proportionality clause may cite), the casewise rank-discrepancy display,
descriptive Spearman rho, and the 79.29% signed share strictly as
separately-labeled reversal accounting. No test, interval, threshold, or
verdict exists anywhere in the clause.

## Phase structure (one contract, right-sizing ruling 2026-09-01)

- **Phase A (this code):** identity gates → provenance-and-join gate →
  census cross-checks → frozen support clause → dictionary-only
  inventory of `clinical_data-description.xlsx` (12,149 bytes, md5
  pinned `c8d806a0…`) with a machine-derived proposed variable freeze.
  Terminal: `PHASE_A_COMPLETE_REQUIRES_AMENDMENT`, or
  `PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED` if the dictionary cannot
  support the minimum variable set. Wall cap: 10 minutes.
- **Amendment + fresh approval:** binds the frozen clinical variable
  list from the dictionary inventory (24-hour NIHSS is the
  lineage-preserving field; admission NIHSS is contextual; center
  mandatory-if-documented) and swaps `required_outputs` to the Phase-B
  interface. Only this fresh approval authorizes staging or reading any
  phenotype byte.
- **Phase B (not implemented here; a later probe-build round under the
  amended blob):** one selective staging event of exactly the **198**
  phenotype members (99 × `demographic_baseline.csv` + 99 ×
  `outcome.csv`) from the held md5-verified `train.7z` (Zenodo record
  16813698), size/CRC-checked against the frozen archive manifest, then
  one aggregate 10-versus-89 estimation table under D4: joint support
  display, per-group missingness, small-cell suppression, and two
  exploratory-labeled uncertainty displays per contrast (deterministic
  leave-one-head-case-out ranges, plus a relabeling range explicitly
  labeled a hypothetical exchangeability reference, seed 20260902).
  Terminal: `STUDY_COMPLETE`.

Blindness is stronger than in v1: no phenotype byte is even staged to
disk until the Phase-B approval exists. **No perfusion map, NCCT, or
lesion-mask member is staged or read in either phase**, the 49 reserved
cases and `sub-stroke0043` are never touched, and
`probes/023/results/results_v2/per_patient.csv` is untouchable by a
path guard.

## What no outcome authorizes

Both terminal statuses are descriptive. The probe defines no
proportionality verdict, no keystone label, no clinically-silent or
clinically-marked reading, no per-patient claim, no model-use or causal
claim, and no generalization beyond the realized 99 cases. The signed
79.29% share may never be compared against the support share as
contribution per unit support.

## Expected sequence

Phase A → record-result → mechanical amendment + fresh approval →
Phase B probe-build → Phase B → record-result → interpret → ratify. An
`ideas/047/registry.yaml` two-node DAG (phase_a → phase_b with the
declared artifact edge) is authored per the registry-per-probe rule.
The v1 draft plan is preserved at commit `63459ec`; the pre-build plan
README at `c81d448`.
