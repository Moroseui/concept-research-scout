# Probe 023 — Stage-0 outcome census

This implements `ideas/023/probe_contract.yaml` version 1. It never trains or
runs a model. Phase S uses synthetic data only; Phase C is mechanically locked
until the Phase-S results are written into the contract and a new hash-bound
human approval is granted.

```bash
python probes/023/run.py --smoke --output-dir /tmp/probe-023-smoke
python probes/023/run.py --phase S --output-dir /path/to/persistent/results
# Only after contract amendment + fresh approval:
python probes/023/run.py --phase C --output-dir /path/to/results \
  --data-dir /path/to/selectively/extracted/train \
  --archive-file /path/to/train.7z --record-json /path/to/zenodo-record.json \
  --phase-s-dir /path/to/approved/phase-s-results
```

Install `requirements.txt` first. Phase C accepts only a training-release path;
any path containing `test` is refused. It deterministically reserves every
non-census patient and never opens their lesion masks. A passing census supports
only the contract's outcome-association prerequisite. It does not authorize
model work or a physiological claim.

For Phase C, selectively extract exactly these release paths for every case:

- `derivatives/**/perfusion-maps/*_space-ncct_{cbf,cbv,mtt,tmax}.nii.gz`
- `derivatives/**/*_lesion-msk.nii.gz` (the release filename keeps
  `ses-0001` even though the file is stored below the follow-up session)
- `rawdata/**/_ncct.nii.gz`

The rawdata NCCT is required: it is not duplicated in `derivatives/`. Raw 4D
CTP and CTA are not used. Keep the output directory on persistent storage.
Phase C writes per-case outcome-blind checkpoints under `phase_c_cache/` and a
per-patient outcome checkpoint after every completed case, so rerunning the
same command resumes after a Colab disconnect. Checkpoints are bound to the
contract, archive, split manifest, and `run.py`; a mismatch exits rather than
silently reusing stale data.

The required CSV/JSON outputs are accompanied by `native_support.svg` and
`identity_residual_distribution.svg`. These dependency-free plots visualize
the same frozen label-blind quantiles recorded in their corresponding CSVs.
