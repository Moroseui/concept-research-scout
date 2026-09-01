# Probe 045 — outcome-blind pooled-slope feasibility probe

`ideas/045/probe_contract.yaml` version 2 was human-approved at contract blob
`5615afea1e2f8309745a2d6558bd9118e5e9f1f3`. It supersedes the executed
version-1 interaction-design contract. The existing `results/results_v2/`
directory remains unchanged as historical evidence from v1.

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

## Run

One command runs the approved real-input feasibility audit:

```bash
python probes/045/run.py --output-dir /path/to/new-results
```

The local synthetic harness check is:

```bash
python probes/045/run.py --smoke --output-dir /tmp/probe-045-v2-smoke
```

Smoke mode writes the same diagnostic/provenance interface, completes without
reading repository outcomes, and is structurally unable to satisfy the
contractual gate. Human approval authorizes this feasibility probe only; even
a pass does not authorize outcome analysis.
