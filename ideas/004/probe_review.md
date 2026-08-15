# Probe code review — idea 004, contract v2

**Verdict: APPROVE.** The revision closes the prior R8 blocker without changing
the scientific scope, endpoints, frozen population, or analysis.

## Blocking findings

None.

## Resolution of the prior blocker

The driver now persists every Phase B attempt in
`sessions/session_attempts.csv` before environment capture, data access, model
loading, or anchor work (`probes/004/run.py:1810-1845`,
`probes/004/run.py:2357-2369`). The record is flushed and `fsync`ed before work
continues. The cap check precedes the append, so attempt 31 exits as budget
exhaustion without beginning or being registered. `summary.json` derives
`sessions_used` from the same registry rather than from the post-anchor
diagnostic log (`probes/004/run.py:2477-2487`). This satisfies the exact repair
required by the preceding review.

The smoke harness independently registers 30 attempts, verifies every row is
durable, refuses attempt 31 with exit 9, and verifies that refusal does not add
a row (`probes/004/run.py:2780-2806`). The operator documentation also states
the accounting rule and identifies the registry as the R8 budget record
(`probes/004/README.md:56-67`).

## Contract and requirements fidelity

- The earlier line-by-line findings remain valid: Phase M is metadata-only;
  Phase B is hash-gated on the amended contract and frozen manifest; the
  manifest is regenerated and checked against the fixed 237/126/58/4 strata;
  no unmanifested scientific volume enters analysis.
- Tier 1 remains per-head and per-stratum on probability and logit scales,
  with no cross-head averaging, patient-cluster bootstrap, and confirmatory
  exclusion of the exposed anchor pair.
- Tier 2 runs only after tier 1, remains per-head/per-stratum, applies the
  preregistered 10-positive/10-negative eligibility rule, reports all excluded
  cells, and introduces no margin, cutoff, operating point, or pass/fail
  semantics.
- Same-session pairing, whole-chunk redo, anchor drift checks, four frozen
  bit-identical spot checks, the r6 dependency closure, and the exactly-one
  `position_ids` exception remain fail-closed.
- The required machine-readable outputs remain represented in the frozen
  bundle layout. The added session registry is budget provenance, not a new
  scientific output or analysis.

## Silent failure, claims, readability, and practicalities

No new silent-failure surface was found. The session record specifically
closes failures occurring before the anchor log exists. Existing checks still
fail explicitly on missing or drifted inputs, selection shortfall, label
mismatch, non-finite scores, model-key mismatch, nondeterminism, anchor drift,
pair splitting, incomplete chunks, and cap overruns.

The result language remains descriptive and checkpoint/contrast/vendor scoped.
The module and README explain phases, stopping, progress, outputs, and Colab
operation; `--output-dir` supports persistent Drive storage and no interactive
prompt is introduced.

Verification performed in this review: `python -m py_compile
probes/004/run.py` passed, and the smoke harness passed every runnable check,
including `session_cap_fail_closed_at_entry`. The analysis portion was skipped
because NumPy is absent in this review environment; this is non-blocking because
NumPy is pinned in `probes/004/requirements.txt:5`, and the README requires a
full smoke rerun after installing the pinned requirements and before a real
phase.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The session cap is now fail-closed at Phase B entry, and the revision preserves the approved scientific scope and analysis."}
```
