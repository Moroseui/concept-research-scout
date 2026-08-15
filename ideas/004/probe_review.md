# Probe code review — idea 004, contract v2

**Verdict: REVISE.** The manifest, inference, and analysis implementation is
substantially faithful, but the session budget is not fail-closed. Phase B can
consume an unlimited number of failed Colab sessions without those sessions
counting toward the contract's cap of 30.

## Blocking finding

### 1. The session cap counts successful anchor-log sessions, not Phase B sessions

Contract R8 freezes a cap of 30 **sessions**. The driver instead reconstructs
usage solely from distinct `session_id` values in `anchor/anchor_log.csv`
(`probes/004/run.py:2321-2329`). A new session is not durably registered at
entry. The anchor log is written only after the model and both anchor inputs
have loaded and all three anchor executions have completed
(`probes/004/run.py:1959-1995`).

Consequently, Phase B sessions that fail during environment capture, metadata
or checkpoint access, checkpoint loading, anchor preprocessing, or anchor
inference do not consume the session cap. The operator can retry those paths
indefinitely while the code continues to report fewer than 30 sessions. This
violates `budgets.session_cap: 30` and the stopping rule requiring the run to
stop when any R8 cap would be exceeded. It is also a silent accounting error:
`summary.json` reports `sessions_used` from the same incomplete anchor-derived
count (`probes/004/run.py:2443-2445`).

Required repair: persist a Phase B session-attempt record before any access,
model, or anchor work, refuse the 31st attempt before it begins, and derive
both enforcement and `sessions_used` from that durable record. Do not expand
the experiment or alter any scientific endpoint.

## Contract fidelity otherwise verified

- Phase M is metadata-only and the current hash-bound approval cannot authorize
  Phase B while the manifest placeholders remain (`probes/004/run.py:431-518`,
  `1627-1747`). The current approval marker matches the contract blob.
- The manifest is regenerated from the pinned metadata, hard-gated at
  237/126/58/4, serialized deterministically, and hash-checked before bulk work
  (`probes/004/run.py:593-741`, `2341-2371`). No unmanifested scientific volume
  enters analysis.
- Canonical direction is fixed independently of row order. Tier 1 is per-head
  and per-stratum on probability and logit scales, excludes the exposed anchor
  from confirmatory summaries, does not summarize across heads, and uses the
  patient-cluster bootstrap (`probes/004/run.py:866-1032`).
- Tier 2 runs only after tier 1, remains per-head/per-stratum, applies the
  preregistered 10-positive/10-negative rule, and reports every excluded cell
  (`probes/004/run.py:1065-1191`, `2274-2309`). It contains no analytical
  margin, cutoff, operating-point, or pass/fail rule.
- Same-session pairing is structural; interrupted chunks are redone in full;
  the four frozen spot-check pairs are rerun bit-identically; and the anchor
  pair is excluded from scientific statistics (`probes/004/run.py:2010-2178`).
- The r6 environment pins and exactly-one `position_ids` exception are
  fail-closed (`probes/004/run.py:1206-1273`, `1462-1538`).
- Required final artifacts are represented in the documented bundle layout,
  including root configuration/provenance/summary files, per-chunk manifests
  and environments, global per-sample/input manifests, both tier tables, and
  the sparse-label exclusion table (`probes/004/run.py:2227-2309`,
  `2437-2484`).

## Silent-failure and claim-discipline review

No second blocking silent-failure surface was found. Empty or drifted inputs,
selection shortfalls, label mismatch, non-finite outputs, model-key mismatch,
within-session nondeterminism, anchor drift, and incomplete chunks all fail
explicitly. Broad exception handlers map failures to non-scientific exit
classes rather than printing a result. The final summary uses the contract's
descriptive outcome language and explicitly prohibits equivalence, robustness,
accuracy, concept-validity, localization, and cross-vendor conclusions
(`probes/004/run.py:2463-2482`).

## Readability and practicalities

The module docstring explains the experiment, phases, stopping rule, outcome
language, and exit codes. Phase comments and progress messages are clear. The
output directory is supplied by `--output-dir`; the launcher design is
non-interactive and suitable for persistent Drive storage.

Non-blocking: `probes/004/README.md:84-87` and
`probes/004/verification.json` say Python compilation and smoke execution were
not possible in the writing sandbox. In this review, `python -m py_compile
probes/004/run.py` passed and the smoke harness completed successfully. The
analysis portion was skipped because NumPy is absent in this review
environment; the README correctly requires rerunning smoke after installing
the pinned requirements before a real phase.

```json
{"verdict": "REVISE", "blocking": ["R8 session accounting derives usage from anchor_log.csv, so any Phase B session that fails before the anchor log is written does not consume the 30-session cap; persist and count every Phase B session attempt at entry and refuse attempt 31 before work begins."], "note": "Scientific scope and analysis are faithful, but the session budget is not fail-closed across retries."}
```
