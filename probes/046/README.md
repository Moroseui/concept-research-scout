# Probe 046 — contribution-definition audit

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

No runner exists yet. Probe code and execution remain prohibited until this
contract has been reviewed and a human approval binds its exact blob.
