# Probe 045 — outcome-blind design feasibility

This directory is reserved for the implementation of
`ideas/045/probe_contract.yaml` version 1. No probe code exists yet, and this
draft does not authorize implementation or execution. The repository coding
gate still requires a reviewed idea card, feasibility memo, probe contract,
and explicit human approval before the probe-code stage.

The probe is deliberately smaller than idea 045's proposed attribution
analysis. It reads the already-imported idea-023 attenuation audit for bands 2
and 3 and reads only `case_id` and `stratum` from `per_patient.csv`. It must
never parse the observed `d` values. Its sole purpose is to determine whether
the frozen band-by-HU-imbalance linear design is full-rank, adequately
conditioned, variable within both bands, and not dominated by a few patients.

The planned implementation has one deterministic CPU-only variant, no random
seed use, no image access, no GPU work, and no access to the 49 reserved cases.
The required outputs are a hashed input manifest, row-level design diagnostics,
aggregate conditioning and leverage diagnostics, the resolved configuration,
environment, summary, and run log.

A passing probe would establish computational estimability only. It would not
estimate the scientific association, test whether attenuation adjustment
changes the parent reversal, validate median HU as tissue type, or authorize a
model-use claim. A valid feasibility failure would require revising the linear
interaction specification before any observed outcome analysis. A malformed
join, unauthorized outcome access, or missing provenance is invalidating and
must not be reported as a negative result.
