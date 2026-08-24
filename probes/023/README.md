# Probe 023 — Stage-0 outcome census

This directory is reserved for the future implementation of
`ideas/023/probe_contract.yaml` (contract version 1). No code has been written
and no probe has been run.

The probe is intentionally smaller than the proposed model study. It tests the
load-bearing prerequisite: whether released ISLES'24 final-infarct labels show
a precise, patient-replicated association with the native joint CBV/MTT state
inside matched relative-CBF deficit strata. It does not train or inspect a
model and does not edit any image.

## Approval sequence

1. **Phase S — synthetic calibration only.** After human approval, simulate
   the frozen patient-clustered estimator to select the support and CI-width
   gates. Real lesion masks and outcome fields are forbidden in this phase.
2. **Contract amendment.** Record the selected thresholds and the simulation
   output SHA-256 in the contract. This changes the contract blob and makes the
   first approval stale.
3. **Phase C — real census.** Only a fresh human approval bound to the amended
   contract may authorize the released-data census.

Even a passing census does not authorize model training, checkpoint download,
counterfactual editing, or inference. Those would require a later contract and
fresh approval.

## Interpretation boundary

A valid positive result establishes only an outcome association in the frozen
census subset. A valid negative result pauses the idea because its keystone is
absent or too imprecise. Missing support, grid or unit incompatibility, mirror
failure, provenance drift, central-volume-coordinate failure, and approval
breaches are invalidating or indeterminate failures—not negative scientific
results.

The probe must not use the phrase “autoregulatory blood-volume reserve,” claim
remaining vasodilatory capacity, attribute a response to CBV rather than MTT,
or say anything about model behavior.
