# Probe 045 — outcome-blind design feasibility

This directory implements the human-approved `ideas/045/probe_contract.yaml`
version 1. Install the single pinned dependency, then use one command:

```bash
python -m pip install -r probes/045/requirements.txt
python probes/045/run.py --output-dir /path/to/probe-045-results
```

The non-scientific harness check is:

```bash
python probes/045/run.py --smoke --output-dir /tmp/probe-045-smoke
```

Smoke uses synthetic rows, includes a sentinel in the forbidden `d` field,
finishes locally, and always reports `SMOKE_ONLY`; it can never satisfy the
contractual gate.

The probe is deliberately smaller than idea 045's proposed attribution
analysis. It reads the already-imported idea-023 attenuation audit for bands 2
and 3 and reads only `case_id` and `stratum` from `per_patient.csv`. It must
never parse the observed `d` values. Its sole purpose is to determine whether
the frozen band-by-HU-imbalance linear design is full-rank, adequately
conditioned, variable within both bands, and not dominated by a few patients.

The implementation has one deterministic CPU-only variant, fixed seed 0, no
image access, no GPU work, no network calls, and no access to the 49 reserved cases.
The required outputs are a hashed input manifest, row-level design diagnostics,
aggregate conditioning and leverage diagnostics, the resolved configuration,
environment, summary, and run log.

A passing probe establishes computational estimability only. It does not
estimate the scientific association, test whether attenuation adjustment
changes the parent reversal, validate median HU as tissue type, or authorize a
model-use claim. A valid feasibility failure would require revising the linear
interaction specification before any observed outcome analysis. A malformed
join, unauthorized outcome access, or missing provenance is invalidating and
must not be reported as a negative result.
