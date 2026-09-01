# Probe 046 — contribution-definition audit

This runner implements the human-approved `ideas/046/probe_contract.yaml`
version 1. It performs one outcome-blind validation pass over the frozen
idea-023 per-patient table. It checks the additive identity and whether every
frozen descriptive definition is well-posed, but never writes case IDs,
scientific values, ranks, shares, means, gaps, or curves.

Run once from the repository root with a new empty output directory:

```bash
python probes/046/run.py --output-dir probes/046/results/results_v1
```

Run the inexpensive synthetic harness check with:

```bash
python probes/046/run.py --smoke --output-dir /tmp/probe-046-smoke
```

Smoke is always `SMOKE_ONLY` and cannot satisfy a contract gate. The real
runner can report only `FEASIBLE_DEFINITION_AUDIT` or
`DEFINITION_REVISION_REQUIRED`. A feasible audit authorizes only drafting a
separate scientific census contract; it says nothing about which cases
dominate or how concentrated the estimator is.

This directory is reserved for the validation-only probe specified by
`ideas/046/probe_contract.yaml` version 1.

The probe's sole purpose is to determine whether the frozen per-case
contribution formula and requested cumulative summaries are algebraically
coherent and numerically well-posed on the exact imported 99-case table. It is
one deterministic, CPU-only variant with no randomness and a five-minute
wall-time cap.

The probe deliberately withholds the scientific result. It must not persist
case identifiers, contribution values, ranks, shares, curve coordinates, band
means, or the band-gap value. It does not run the proposed contribution census,
read phenotype outcomes, access reserved cases, or support carrier, biological,
clinical, causal, predictive, or model-use claims.

The runner now exists under the human approval bound to the exact contract
blob. This implementation does not itself authorize the later scientific
census described by the idea card.
