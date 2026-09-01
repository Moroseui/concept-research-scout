# Probe 046 — finite-population contribution census

The human-approved `ideas/046/probe_contract.yaml` is contract version 2. It
specifies one deterministic, CPU-only census of the 99 observed case
contributions to idea-023's realized band-3-minus-band-2 estimator.

Run the census once into a new, empty output directory:

```bash
python probes/046/run.py --output-dir /path/to/probe-046-v2-output
```

Run the synthetic harness check without reading the real table:

```bash
python probes/046/run.py --smoke --output-dir /tmp/probe-046-smoke
```

The proposed v2 run would emit:

- all 99 signed per-case contributions;
- the complete signed cumulative contribution sequence;
- the complete absolute-contribution Lorenz curve;
- fixed top-k summaries for k = 1, 5, 10, and 20; and
- the smallest positive-contribution prefixes reaching 50% and 80% of
  observed positive mass.

The census deliberately defines no diffuse-versus-concentrated classifier,
null model, confidence interval, or stable-carrier label. Every valid curve
shape is reported as a finite-population description. It reads no phenotype
file, reserved case, raw image, voxel array, or cache, and it supports no
biological, clinical, causal, predictive, population, or model-use claim.

`CENSUS_COMPLETE` is descriptive only. It is not a diffuse-versus-concentrated
classification and supports no stable-carrier, biological, clinical, causal,
predictive, population, or model-use claim. The previous v1 result remains
unchanged in `probes/046/results/results_v2/`.
