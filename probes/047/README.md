# Probe 047 — keystone-ten support arithmetic and clinical profile (contract v1, draft)

`ideas/047/probe_contract.yaml` (contract_version 1, not yet approved)
specifies one CPU-only, two-phase pipeline for idea 047. No code exists
yet; this README records the plan the contract binds. Probe code may be
written only after probe review and explicit human approval of the
contract blob.

## What the probe tests first (the riskiest assumption)

Before any science is emitted, Phase A must reproduce, by exact integer
equality, all 297 cached per-band `q1_voxels`/`q4_voxels` values in
`probes/023/results/results_v2/per_patient.csv` (sha256 `1d01551c…`),
by re-running the frozen take-13 region machinery
(`probes/023/run.py`, git blob `0e9a40b453b6d4b653841d6ea70f2e4b75cce9be`)
lesion-free on restaged maps: `load_case(load_label=False)` →
`coordinate_arrays` (Tmax>6.0 deficit, erosion, border + two-voxel
array-midline exclusion, per-patient p98 CBV vessel rule, finiteness) →
`flow_band_labels` → per-band `z=log(CBV)` quartile cuts
(`np.quantile(z,[0.25,0.75])`) → counts of `z<=q1` / `z>=q3`.
A 297/297 pass licenses `B_i` — the eligible-region voxel count, which
the frozen code guarantees equals the sum of the three band member
counts — as the take-13 region rather than a variant. Any mismatch
stops the run as `REPRODUCIBILITY_GATE_FAILURE` with a per-row report
plus an environment comparison; no support output is written and no
variant region may be substituted (operator ruling,
`ideas/047/unblock_ack.txt`).

## Phase structure (one contract, right-sizing ruling 2026-09-01)

- **Phase A (phenotype-blind):** dictionary-only inventory of
  `clinical_data-description.xlsx` and a machine-derived proposed
  variable freeze, hashed before any map byte is read; one selective
  staging event; the reproducibility gate; then the frozen
  finite-population support clause — `sum_head |c_i| / sum_all |c_i|`
  beside `sum_head B_i / sum_all B_i`, rank-discrepancy display,
  descriptive Spearman rho, and the 79.29% signed share only as
  labeled reversal accounting. Terminal:
  `PHASE_A_COMPLETE_REQUIRES_AMENDMENT` (or
  `PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED` if the dictionary cannot
  support the minimum variable set).
- **Amendment + fresh approval:** binds the frozen clinical variable
  list from the dictionary inventory and swaps `required_outputs` to
  the Phase-B interface. Only this fresh approval authorizes reading
  any phenotype row.
- **Phase B (clinical):** opens exactly the 99 analyzed cases'
  phenotype files under the ratified D3 read-restriction and emits one
  aggregate 10-versus-89 estimation table under D4 (joint support
  display, exploratory-labeled null-reference ranges, seed 20260902,
  small-cell suppression, no per-case clinical values). Terminal:
  `STUDY_COMPLETE`.

## Exact extraction set (693 members)

For each of the 99 analyzed case ids in
`probes/046/results/results_v3/per_case_contributions.csv`
(sha256 `aba52512…`), from the held md5-verified `train.7z`
(Zenodo record 16813698, md5 `36ae28b9a17f7340b8bbef62b595cb57`):

- `train/derivatives/<id>/ses-01/perfusion-maps/<id>_ses-01_space-ncct_{tmax,cbf,cbv,mtt}.nii.gz` (4 × 99)
- `train/raw_data/<id>/ses-01/<id>_ses-01_ncct.nii.gz` (99; required by the frozen loader)
- `train/phenotype/<id>/ses-01/<id>_ses-01_demographic_baseline.csv` (99)
- `train/phenotype/<id>/ses-02/<id>_ses-02_outcome.csv` (99)

plus `clinical_data-description.xlsx` fetched from the record itself.
Member discovery tolerates the `sub-stroke`/`sub-strokecase` and
`raw_data`/`rawdata` spellings. **No lesion-mask member is ever
extracted or read in either phase.** The 49 reserved cases and the
excluded `sub-stroke0043` are never touched. Phenotype bytes staged in
Phase A remain unread until the Phase-B approval; an earlier read is
invalidating.

## What no outcome authorizes

Both terminal statuses are descriptive. The probe defines no
proportionality verdict, no keystone label, no clinically-silent or
clinically-marked reading, no per-patient claim, no model-use or causal
claim, and no generalization beyond the realized 99 cases. The signed
79.29% share may never be compared against the support share as
contribution per unit support.

## Expected sequence

probe review → human approval of contract v1 → probe-build (`run.py`
here, environment pinned per `probes/023/requirements.txt`) → Phase A →
record-result (bundle to `probes/047/results/results_v2`) → mechanical
amendment + fresh approval → Phase B → record-result
(`probes/047/results/results_v3`) → interpret → ratify. A
`ideas/047/registry.yaml` two-node DAG (phase_a → phase_b with the
declared artifact edge) is authored at approval per the
registry-per-probe rule.
