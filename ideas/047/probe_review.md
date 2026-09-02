# Probe code review — idea 047, contract v2, Phase A, revision round 2

## Verdict

**APPROVE.** The revision closes all three prior blockers without changing the
scientific scope. Phase A implements the approved support-share arithmetic on
the frozen 99-case cohort, preserves the phenotype boundary, writes the
contract-required interface, and labels every terminal result within the
contract's descriptive claim ceiling. No `ideas/047/contract_requirements.md`
exists, so the requirements-governed tier/head/manifest checks do not apply.

## Blocking findings

None.

## Resolution of the prior blocking findings

- **Hard standard 4 — resolved.** A real run now requires a pre-staged
  `--dictionary-file` and refuses when it is absent
  (`probes/047/run.py:205-211`, `probes/047/run.py:1073-1080`). The held file is
  checked against the frozen byte-count and MD5 pins before parsing
  (`probes/047/run.py:710-735`). The remaining Zenodo URL is provenance text,
  not an executed fetch (`probes/047/run.py:102-105`); no network-capable
  import or call remains. The operator command documents the required offline
  input (`probes/047/README.md:11-24`).
- **Hard standard 5 — resolved.** Before the outcome-derived contribution
  table or census summary is opened, the code pin-verifies and reads only the
  phenotype-blind exclusions table, writes the actual analyzed case IDs plus
  the two bookkeeping exclusions to `split_manifest.csv`, and hashes that
  manifest (`probes/047/run.py:294-333`, `probes/047/run.py:1090-1110`). After
  contribution access, the support gate requires exact equality between its
  IDs and the frozen split IDs and records the split hash in the gate artifact
  (`probes/047/run.py:456-483`, `probes/047/run.py:515-522`). A count-preserving
  case substitution therefore fails visibly.
- **Hard standard 1 — resolved.** Both determinism manifests cover the three
  frozen tables, frozen take-13 source, pre-staged dictionary, seed, mode, and
  parsed row counts (`probes/047/run.py:1089-1127`). The common finalizer
  re-hashes those inputs, requires exact start/end equality, writes the end
  manifest, and runs on both normal completion and the registered
  `SUPPORT_PROVENANCE_FAILURE` path (`probes/047/run.py:1024-1039`,
  `probes/047/run.py:1144-1159`, `probes/047/run.py:1286-1289`).

## Contract fidelity and silent-failure review

- The analysis uses exactly the frozen signed-rank top ten and 99-case input,
  computes the sole authorized comparison—absolute-contribution share beside
  eligible-support share—and keeps the signed share in a separately labeled
  reversal-accounting field (`probes/047/run.py:614-699`,
  `probes/047/run.py:1178-1205`). No support-clause hypothesis test, interval,
  residual subgroup, or model analysis is present.
- Input pins, exact row/ID/rank structure, finite values, bookkeeping rows,
  census identities, and output arithmetic fail closed
  (`probes/047/run.py:343-385`, `probes/047/run.py:399-532`,
  `probes/047/run.py:543-699`). The provenance-stop path writes no scientific
  support output and calls itself a decision-grade stop, not a negative
  (`probes/047/run.py:1144-1159`).
- The normal path writes every Phase-A `required_outputs` artifact named by
  the contract (`probes/047/run.py:1186-1221`, `probes/047/run.py:1240-1309`).
  `per_case_support.csv` is the contract's concrete per-case output; the
  generic stage-task reference to `per_sample.csv` does not override the
  approved interface.
- Limits are explicit and respected: one variant, zero GPU minutes, one
  declared seed, and a 600-second Phase-A wall cap
  (`probes/047/run.py:65-72`, `probes/047/run.py:1178-1181`,
  `probes/047/run.py:1236-1244`). Phase B is unreachable because this code
  requires the pre-amendment sentinel and current approval binding
  (`probes/047/run.py:264-285`).

## Hard standards and practical verification

- **Standard 2:** `probe_exclusions.csv` records both non-analyzed cases with
  record type and reason (`probes/047/run.py:1136-1142`).
- **Standard 3:** transforms carry explicit checks or assertions for table
  identity, contribution algebra, ranks, shares, dictionary staging/parsing,
  and smoke construction (`probes/047/run.py:399-699`,
  `probes/047/run.py:710-856`, `probes/047/run.py:859-1010`).
- **Standard 6:** `python3 probes/047/run.py --smoke --output-dir <new-dir>`
  completed with exit 0 in under one second in this review. It emitted
  `SMOKE_ONLY`, start/end manifests compared equal, and the dictionary was
  present in both manifests. Smoke uses 12 synthetic cases and a three-case
  head, skips approval, and cannot emit a contractual Phase-A terminal
  (`probes/047/run.py:859-930`, `probes/047/run.py:1065-1072`,
  `probes/047/run.py:1224-1234`).
- `python3 -m py_compile probes/047/run.py` passed. Requirements are standard
  library only, paths are explicit, output is controlled by `--output-dir`,
  and there are no prompts or GPU dependencies (`probes/047/requirements.txt`,
  `probes/047/run.py:199-212`).

## Non-blocking findings

- Several transform invariants use Python `assert` and would disappear under
  `python -O` (`probes/047/run.py:406`, `probes/047/run.py:451-452`,
  `probes/047/run.py:616-665`, `probes/047/run.py:1214-1216`). The documented
  command does not enable optimization, and surrounding pin/shape/cross-check
  gates cover the claim-bearing structure, so this does not block this bounded
  probe. Explicit fail-closed checks would nevertheless be preferable in a
  future neutral hardening pass.
- The registered provenance-stop path intentionally emits a reduced interface
  rather than all normal Phase-A outputs. This matches the contract's statement
  that the gate record is the stop deliverable and does not masquerade as a
  completed Phase-A bundle.

```json
{"verdict": "APPROVE", "blocking": [], "note": "All prior blockers are closed; smoke and compilation pass, and Phase A is contract-faithful, offline, split-bound before outcome access, and determinism-complete on every registered terminal path."}
```
