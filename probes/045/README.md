# Probe 045 — v3 pooled-slope attenuation attribution

This runner implements the human-approved `ideas/045/probe_contract.yaml`
version 3. It reads the already-open 99-case outcome table exactly once and
fits one model:

`d = intercept + band-3 indicator + pooled-mean-centered HU imbalance`

Run from the repository root with a new output directory:

```bash
python probes/045/run.py --output-dir probes/045/results/results_v4
```

The runner refuses an output directory that already contains scientific
outputs, verifies the two frozen input hashes and the approval-bound contract
blob, writes the split before opening the outcome file, keeps both band rows
together in 10,000 patient-cluster bootstrap draws, and records every dropped
band-1 row in `exclusions.csv`. It makes no network calls and uses no GPU.

For the inexpensive harness check:

```bash
python probes/045/run.py --smoke --output-dir /tmp/probe-045-smoke
```

Smoke uses tiny synthetic inputs and 40 bootstrap draws. Its status is always
`SMOKE_ONLY`; it cannot satisfy any scientific result class.

The three possible valid real-run classifications are exactly the contract's
`DECISIVE_MEASURED_EXPLANATION_FAILURE`,
`ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION`, and `SENSITIVITY_LIMITED`.
They are bounded to this measured median-HU proxy in these 99 cases. The run
does not establish causation, validate tissue type or viability, test a model,
or authorize access to the 49 reserved cases.

Historical `results_v2/` and `results_v3/` are immutable outputs of the two
completed outcome-blind feasibility contracts. Do not use either as the v3
output directory.
