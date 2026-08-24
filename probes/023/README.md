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
  --archive-file /path/to/train.7z --record-json /path/to/zenodo-record.json
```

Install `requirements.txt` first. Phase C accepts only a training-release path;
any path containing `test` is refused. It deterministically reserves every
non-census patient and never opens their lesion masks. A passing census supports
only the contract's outcome-association prerequisite. It does not authorize
model work or a physiological claim.
