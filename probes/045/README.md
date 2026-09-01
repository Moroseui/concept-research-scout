# Probe 045 — outcome-blind pooled-slope feasibility draft

`ideas/045/probe_contract.yaml` version 2 is a draft for human review. It
supersedes the executed version-1 interaction-design contract, but it does not
authorize code changes or execution. The existing `run.py`, requirements,
verification receipt, and `results/results_v2/` belong to v1 and must remain
unchanged as historical evidence.

## Smallest probe

Version 1 established that the four-column band-by-HU-imbalance interaction
design was full-rank but failed its frozen conditioning, band-2 support,
leverage, and leave-one-patient-out gates. Version 2 tests one narrower
specification only: a three-column design containing an intercept, a band-3
indicator, and pooled centered Q1-minus-Q4 median-HU imbalance. It omits the
interaction term.

The proposed probe is deterministic, CPU-only, one variant, and outcome-blind.
It uses the same two hash-pinned idea-023 tables and may read only `case_id` and
`stratum` from `per_patient.csv`; parsing any observed `d` value is an
invalidating failure. It recomputes row accounting, rank, condition number,
exposure support, leverage, and complete leave-one-patient-out diagnostics.
The 49 reserved cases remain untouched.

## Interpretation boundary

A pass means only that the reduced design is numerically feasible. It cannot
show that a common HU-imbalance slope is scientifically correct, that HU
imbalance is associated with final infarction, or that tissue composition
explains the parent reversal. Those questions require a separate contract and
fresh human approval.

A valid failure is a decisive negative for this pooled-slope specification
only. Unauthorized outcome access, input drift, join errors, nonfinite
diagnostics, analysis drift, or missing provenance invalidate the run and are
not negative scientific results.

Before any implementation work, the human must resolve the contract's open
scientific-model question: whether replacing band-specific slopes with one
pooled slope preserves enough of the attribution question to justify a later
outcome analysis. After that decision, v2 still requires fresh contract
approval and a new probe-code review; the v1 approval marker does not authorize
v2.
