# Probe 047 — keystone-ten support arithmetic and clinical profile

**Position (2026-09-02): Phase A complete and ratified; contract v3
(the pre-registered Phase-B amendment) drafted and awaiting fresh human
approval. Phase-B code is not yet implemented.**

Phase A executed under contract v2 (blob
`b4887c05a21bfe870589b5d9982066943df679d5`) and is **of record**:
terminal `PHASE_A_COMPLETE_REQUIRES_AMENDMENT`, bundle imported at
`probes/047/results/results_v2` (commit `6037f24`), interpretation
cross-family reviewed (APPROVE) and ratified. The Phase-A bundle
validates under its own historical blob forever; nothing re-authorizes
Phase-A execution.

`ideas/047/probe_contract.yaml` is now **contract v3**, the amendment
v2's own `amendment_protocol` pre-registered: it binds the frozen
clinical variable list from Phase A's machine-derived proposal
(`proposed_variable_freeze.json`, sha256 `87c5e11b…`), records the
Phase-A consumed artifacts, and swaps `required_outputs` to the Phase-B
interface. The blob change stales the Phase-A approval by construction;
fresh human approval of the v3 blob is the sole authorization for
Phase B, for staging any phenotype member, and for the first read of
any phenotype row.

`run.py` in this directory implements **Phase A only** and refuses the
amended contract by construction (its authority gate requires the
pre-amendment `frozen_variable_list` sentinel). It is retained as the
frozen implementation of record; Phase-B code arrives in a later
probe-build round under the approved v3 blob.

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
- **Amendment (contract v3, DRAFTED, awaiting fresh approval):** binds
  the seven-variable frozen clinical list from Phase A's machine
  proposal — MRS 3 months (ordinal, primary outcome), NIHSS 24h
  (continuous, the lineage-preserving field), NIHSS at admission
  (continuous, baseline context, never interchangeable with 24h), Age
  (continuous), Sex (binary), and the two contextual-cap fields mTici
  postinterventional (ordinal, frozen mTICI level order) and Onset to
  door (continuous minutes) — with exact release spellings, parse/
  missingness rules, and closed-menu statistics per variable. Center is
  absent from the dictionary; the mandatory-if-documented rule is
  discharged by that recorded absence. `required_outputs` is swapped to
  the Phase-B interface; the Phase-A bundle identity plus the hashes of
  `proposed_variable_freeze.json` and `per_case_support.csv` are bound
  as consumed artifacts.
- **Phase B (not implemented here; a later probe-build round under the
  approved v3 blob):** one selective staging event of exactly the
  **198** phenotype members (99 × `demographic_baseline.csv` + 99 ×
  `outcome.csv`) from the held md5-verified `train.7z` (Zenodo record
  16813698), size/CRC-checked against the frozen archive manifest;
  then the pre-registered phenotype schema/missingness census
  (feasibility section 8) with the decision-grade stop
  `PHENOTYPE_SCHEMA_MISMATCH` if the case-level rows cannot support
  the minimum variable set; then one aggregate 10-versus-89 estimation
  table under D4: joint support display, per-group missingness,
  small-cell suppression, and two exploratory-labeled uncertainty
  displays per contrast (deterministic leave-one-head-case-out ranges,
  plus a relabeling range explicitly labeled a hypothetical
  exchangeability reference, seed 20260902). Terminal:
  `STUDY_COMPLETE`.

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

Phase A ✓ → record-result ✓ → interpret + cross-family review ✓ →
ratify ✓ → **amendment (contract v3, this round) → fresh human
approval** → Phase B probe-build + cross-family review → Phase B run →
record-result (expected destination `probes/047/results/results_v3`
per the current-blob discovery convention) → interpret → ratify. An
`ideas/047/registry.yaml` two-node DAG (phase_a → phase_b with the
declared consumed-artifact edge) remains queued per the
registry-per-probe rule, to be authored before or alongside the
Phase-B record-result. The v1 draft plan is preserved at commit
`63459ec`; the v2 plan at `c2e5576`; the pre-build plan README at
`c81d448`.
