# Probe 046 — finite-population contribution census

The current draft `ideas/046/probe_contract.yaml` is contract version 2. It
specifies one deterministic, CPU-only census of the 99 observed case
contributions to idea-023's realized band-3-minus-band-2 estimator.

Version 2 is a draft. It has not been human-approved and authorizes neither
code changes nor execution. The existing `run.py`, `requirements.txt`,
`verification.json`, and `results/results_v2/` belong to the completed,
human-approved version 1 definition audit. They must not be modified or
represented as version 2 outputs.

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

If the v2 contract receives fresh human approval, probe code must be built and
cross-family reviewed in a later stage before any execution. No v2 command
exists yet.
