# Probe code review — idea 004 (load probe, contract v1) — ROUND 4

**Reviewed artifacts:** `probes/004/run.py` (revision `759b664`),
`probes/004/requirements.txt`, `probes/004/README.md`,
`probes/004/verification.json`, and `ideas/004/probe_contract.yaml`.
This review is limited to the decision-ledger-authorized exit-7 repair: kernel
normalization, selection diagnostics, and manifest provenance. The previously
approved one-pair, three-execution probe remains unchanged.

**Verdict: APPROVE.** The repair fixes the observed predicate drift without
expanding the experiment. I independently compiled the script and ran
`python probes/004/run.py --smoke --output-dir <temporary-directory>`; it
completed successfully, wrote all required smoke artifacts including the new
`selection_audit.json`, produced 54 per-head rows, and retained the explicit
`contract_satisfied: false` smoke interpretation.

## Contract fidelity

- **No scope or cap drift.** The real path still selects exactly one
  predeclared validation pair and runs A, B, A-repeat only. The 45-minute,
  three-execution, one-seed gates and the diagnostic-only treatment of A-vs-B
  differences are unchanged (`run.py:982-1002`, `run.py:1141-1194`).
- **Kernel repair matches the ledger.** `normalize_kernel` strips a raw string
  and, for a parsable list literal, uses element 0; selection applies that
  function only to Br40f/Br60f membership (`run.py:376-397`,
  `run.py:477-483`). Geometry fields remain exact row-to-row comparisons
  (`run.py:491-502`).
- **Required outputs are covered.** `selection_audit.json` was added to the
  contract and documentation. Real mode writes it before enforcing the frozen
  237-pair count, so an exit-7 mismatch leaves the diagnostic artifact behind
  (`run.py:986-998`). Successful real mode still writes the other required
  artifacts through the previously approved paths.
- **Manifest provenance is faithful.** Each selected volume's raw and
  normalized kernel values come from its own metadata row, rather than from a
  role-based constant (`run.py:557-568`).

## Silent-failure review

No blocking silent-failure surface was introduced. A count differing from 237
still stops before volume inference. Before that stop, the code writes the
top-ten raw kernel values with counts, normalized values and example volume
names, plus per-filter drop counts, to both the JSON audit and run log
(`run.py:437-455`, `run.py:468-507`, `run.py:535-550`, `run.py:986-998`). The
smoke test asserts the exact planted-decoy drop counts and verifies both the
list-form and plain-string paths (`run.py:715-764`).

The independent smoke run confirmed that `"['Br40f', '3']"` and
`"['Br60f', '3']"` select the intended pair, while slice-count and spacing
decoys are rejected. The generated audit reported five validation scans, two
missing-contrast drops, two geometry drops, and the expected per-column
mismatch counts.

## Claim discipline and readability

The summary language remains contract-correct: smoke mode cannot satisfy the
contract, and a real passing run authorizes only a request for a later bulk
contract. The new module and phase comments explain the exit-7 cause and the
normalization provenance. No test split, extra pair, threshold, margin, or
scientific reconstruction-sensitivity analysis was added.

## Non-blocking findings

1. **Reruns still overwrite an existing output directory.** `run_log.txt` is
   truncated and artifacts are rewritten in place (`run.py:1218-1219`). This
   was carried from the prior approved revision; use a fresh persistent output
   directory for each real attempt.
2. **Committed verification text understates current verification.** The
   bundled `verification.json` says the revised smoke run could not be
   executed in the coder's sandbox. This review independently executed it
   successfully, so that historical statement is no longer a project-level
   uncertainty and does not require a code change.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The exit-7 repair faithfully normalizes list-form kernels, emits pre-failure selection diagnostics, records row-derived kernel provenance, and passes an independent smoke run without scope or cap drift."}
```
