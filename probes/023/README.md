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
- `derivatives/**/*_lesion-msk.nii.gz`
- `{raw_data,rawdata}/**/*_ncct.nii.gz`

The payload manifest, not the release-description example, defines the case
set. The runner accepts both observed `sub-strokeNNNN` and documented
`sub-strokecaseNNNN` identifiers, both `raw_data/` and `rawdata/`, and the
session spelling present in each member path. If the archive contains a
byte-identical duplicate lesion member, one lexicographically selected member
is retained and every extra row is named in both `schema_census.csv` and
`exclusions.csv`; non-identical duplicates stop as a population failure.

The rawdata NCCT is required: it is not duplicated in `derivatives/`. Raw 4D
CTP and CTA are not used. Keep the output directory on persistent storage.
CBV units are not documented in the released payload or inspected dataset
descriptions. The amended contract therefore excludes vessel-like voxels above
each patient's 98th percentile of finite positive CBV; `identity.json` records
this evidence and `exclusions.csv` records each patient's threshold.
Phase C writes per-case outcome-blind checkpoints under `phase_c_cache/` and a
per-patient outcome checkpoint after every completed case, so rerunning the
same command resumes after a Colab disconnect. Checkpoints are bound to the
contract, archive, split manifest, and `run.py`; a mismatch exits rather than
silently reusing stale data.

The required CSV/JSON outputs are accompanied by `native_support.svg` and
`identity_residual_distribution.svg`. These dependency-free plots visualize
the same frozen label-blind quantiles recorded in their corresponding CSVs.
