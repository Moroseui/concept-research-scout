# Probe 045 — pooled-slope attenuation attribution

The current draft is `ideas/045/probe_contract.yaml` version 3. It proposes
the smallest outcome-reading analysis justified by the completed v2
feasibility result. It is not approved, and no v3 code or execution is
authorized.

## What it tests

The probe asks whether the already-computed patient-level Q1-minus-Q4 median
NCCT attenuation imbalance accounts for idea-023's opposite-signed mean
final-infarct contrasts in flow bands 2 and 3. It uses one prespecified model:

`d = intercept + band-3 indicator + centered HU imbalance`

The model is fit once on the same 99 already-analyzed patients (198 band
rows). Uncertainty comes from a fixed 10,000-replicate patient-cluster
bootstrap. Both rows for a patient remain together in every resample.

## Why this is the smallest next probe

Version 1 showed that the more direct band-by-imbalance interaction design
was numerically fragile. Version 2 established that the reduced common-slope
design is well conditioned and not dominated by one patient, without reading
any outcome value. Version 3 would read outcomes only to answer the remaining
attribution question. It adds no images, models, thresholds, subgroups, or
alternative specifications and leaves the 49 reserved cases untouched.

## Interpretation boundary

Three outcomes are frozen in advance:

- `ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION`: the pooled HU slope interval
  excludes zero and adjustment breaks the parent's decisive opposite-sign
  conjunction. This is observational compatibility, not causation.
- `DECISIVE_MEASURED_EXPLANATION_FAILURE`: adjusted band 2 remains below zero
  and adjusted band 3 above zero, with both clustered-bootstrap intervals
  excluding zero. This rejects only the measured median-HU explanation.
- `SENSITIVITY_LIMITED`: every other valid result. It is not evidence of no
  association.

The probe cannot validate median HU as tissue type or viability, establish
model use, or generalize beyond the frozen 99-case cohort and released
pipeline.

## Authority and lineage

The existing `results/results_v2/` and `results/results_v3/` directories are
immutable evidence from the completed v1 and v2 feasibility contracts. A v3
implementation must write to a new result directory and pass a fresh probe
review. Execution requires explicit human approval bound to the exact v3
contract blob. Until then, do not write probe code and do not read `d`.
