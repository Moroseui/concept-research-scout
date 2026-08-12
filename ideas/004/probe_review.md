# Probe code review — idea 004 (load probe, contract v1) — ROUND 6

**Reviewed artifacts:** `probes/004/run.py`, `probes/004/requirements.txt`,
`probes/004/README.md`, `ideas/004/probe_contract.yaml`, and the 2026-08-12 r6
decision-ledger authorization. This review is limited to the authorized r6 repair:
restore the previously installable Transformers closure and tolerate exactly the
enumerated framework-era `*.embeddings.position_ids` buffer key while preserving
strict loading for everything else.

**Verdict: APPROVE.** The repair implements the ledger specification without
expanding the experiment or concealing checkpoint incompatibility. I compiled
`run.py`, ran its smoke mode into a fresh temporary output directory, and confirmed
all eight required artifacts, 54 per-head rows, and `contract_satisfied: false`.

## Contract fidelity

- **The authorized compatibility exception is exact and fail-closed.** The regex
  is suffix-anchored and requires a leading component
  (`probes/004/run.py:626-643`). The real load requires exactly one matching key;
  zero or multiple matches exit 5, and `strict=True` still rejects every other
  missing or unexpected key (`probes/004/run.py:1174-1203`). This matches the r6
  ledger's updated meaning of “unchanged modulo enumerated, provenance-logged
  framework-era buffer keys.”
- **The exception is auditable.** The removed key, pattern, and reason are written
  to `provenance.json` before strict loading and printed to the run log
  (`probes/004/run.py:1186-1199`). The installed Transformers version is captured
  in `environment.txt` and logged at startup (`probes/004/run.py:335-353`).
- **No experiment-scope drift.** Pair selection, the A/B/A execution sequence,
  one-seed limit, 45-minute cap, 18-output checks, bit-determinism check, and
  required outputs remain intact. The dependency closure is restored to
  `transformers==4.38.2` and `tokenizers==0.15.2` as directed
  (`probes/004/requirements.txt:8-16`).

## Silent-failure surfaces

No blocking silent-failure surface was found. The buffer strip cannot silently
generalize to arbitrary checkpoint differences: near-miss names remain untouched,
and strict loading follows immediately. Smoke mode explicitly tests the observed
key, near misses, and zero/two-match behavior (`probes/004/run.py:802-832`). Any
other load problem remains an exit-5 failure rather than a successful result.

## Claim discipline

The summary describes success as strict loading **modulo the one enumerated key**
and continues to label A-versus-B differences scientifically uninterpretable
(`probes/004/run.py:1288-1327`). Smoke mode cannot satisfy the contract and says so
in `summary.json` (`probes/004/run.py:908-945`). No new data, execution, head
selection, threshold, or scientific analysis was added.

## Readability and practicalities

The module docstring and README explain why the old pin cannot install on Colab
Python 3.12, what key is removed, why that key is non-learnable, and which failures
remain fatal (`probes/004/run.py:23-38`; `probes/004/README.md:66-84`). The smoke
run completed successfully and wrote `resolved_config.json`, `per_sample.csv`,
`summary.json`, `environment.txt`, `provenance.json`, `input_manifest.csv`,
`selection_audit.json`, and `run_log.txt` to the supplied `--output-dir`.

## Non-blocking findings

1. **The real checkpoint result remains unknown by design.** The smoke test proves
   only harness behavior; only the approved real run can establish whether the
   checkpoint contains exactly the understood buffer key and otherwise loads
   strictly.
2. **The README's verification note is stale.** It says the implementation sandbox
   could not execute Python (`probes/004/README.md:86-88`), whereas this review
   successfully compiled and smoke-tested the driver. This does not affect probe
   execution or interpretation.
3. **No full Colab dependency installation was repeated in this review.** The r6
   closure is the ledger-designated return to the version set previously installed
   successfully twice; the decisive practical check remains the human's Colab
   installation and real run.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The r6 repair tolerates only the single provenance-logged framework-era position_ids buffer key, preserves strict loading and the approved probe scope, and passes compilation plus the complete smoke harness."}
```
