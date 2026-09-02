# Probe code review — idea 047, contract v2, Phase A

## Verdict

**REVISE.** The support arithmetic, frozen cohort size, head definition, output labels, variant/GPU/seed limits, and Phase-A/Phase-B authority boundary are faithful to the approved contract. The synthetic smoke run completed successfully in under one second and terminated as `SMOKE_ONLY`. Three hard-code-standard failures remain blocking.

No `ideas/047/contract_requirements.md` exists, so the requirements-governed tier/head/manifest checks do not apply.

## Blocking findings

### B1 — The default real run performs analysis-time network access (Hard standard 4)

`run.py` makes `--dictionary-file` optional and, when it is absent, imports `urllib.request` and fetches the workbook during the scientific run (`probes/047/run.py:220-227`, `probes/047/run.py:673-698`). The standards require paths and seeds to be declared with **no analysis-time network**. The immutable URL, byte count, and MD5 make this fetch pinned, but they do not make it offline or remove transport state from the run. The default command documented for the operator uses this network path (`probes/047/README.md:13-23`).

Required revision: make the checksum-verified dictionary a required pre-staged input to the probe and refuse if it is absent. Keep the same record, file, byte-count, and digest pins; do not broaden the staging scope.

### B2 — The pre-outcome split manifest does not bind the frozen cases (Hard standard 5)

The manifest written before input access contains only anonymous integers 1 through 99 (`probes/047/run.py:295-315`). It does not contain or hash the frozen 99 `case_id` values. The actual identities are first learned later from the outcome-derived contribution table (`probes/047/run.py:389-432`, invoked at `probes/047/run.py:1048-1053`). Consequently, `split_manifest_sha256` proves only that 99 placeholder rows existed before outcome access; it cannot prove which cases constituted the split or detect a case substitution while preserving the count.

Required revision: before opening the contribution/outcome-derived table, construct and hash a case-identified split manifest from the pinned phenotype-blind analyzed-case rows in `exclusions.csv`, including the reserved/excluded policy, then require exact equality to the contribution IDs after that table is opened. The support gate's later set comparison is useful but does not retroactively satisfy the before-access freeze.

### B3 — Start/end determinism manifests are incomplete and absent on the registered stop path (Hard standard 1)

On successful completion, the start and end manifests cover the three repository tables and frozen source file and are compared (`probes/047/run.py:1041-1053`, `probes/047/run.py:1208-1216`). They do not include the clinical dictionary, even though it determines `dictionary_inventory.csv`, `proposed_variable_freeze.json`, and the terminal status; that input is acquired only after the start manifest and appears solely in other provenance (`probes/047/run.py:1130-1142`, `probes/047/run.py:1178-1186`). Thus the manifests that claim start/end agreement omit a claim-bearing input.

Further, the pre-registered `SUPPORT_PROVENANCE_FAILURE` return writes neither `determinism_manifest_end.json` nor an equality check (`probes/047/run.py:1068-1082`). Hard standard 1 requires start/end manifests to be present and agreeing; the decision-grade stop is an authorized terminal path whose evidence must also be reproducible.

Required revision: include every probe input, including the required pre-staged dictionary, in both manifests and compare them. Finalize the end manifest and its equality result before returning from every registered terminal path, including `SUPPORT_PROVENANCE_FAILURE`. A failure before a start manifest can still fail loudly; it must not masquerade as a completed or decision-grade bundle.

## Non-blocking findings

- Contract fidelity is otherwise strong. The code uses exactly 99 frozen cases and signed ranks 1–10, computes the absolute-contribution share against eligible-support share, keeps the signed share separately labeled, and performs no inferential test in the support clause (`probes/047/run.py:507-662`, `probes/047/run.py:1101-1128`).
- The code writes every Phase-A `required_outputs` artifact on a valid completion. The stage-task template mentions `per_sample.csv`, but the governing contract's concrete interface instead requires `per_case_support.csv`; the implementation correctly follows the approved contract (`probes/047/run.py:1109-1243`).
- Missing, malformed, duplicate, nonfinite, and identity-mismatched inputs generally fail loudly. The support-provenance stop writes its discrepancies without emitting support results (`probes/047/run.py:435-496`, `probes/047/run.py:1068-1082`).
- The exclusions log records the two non-analyzed bookkeeping cases and their reasons (`probes/047/run.py:1062-1067`), satisfying Hard standard 2 for this phase.
- Data transforms have explicit checks or assertions, and the central file/row/rank/share transforms are guarded (`probes/047/run.py:378-432`, `probes/047/run.py:435-496`, `probes/047/run.py:578-629`, `probes/047/run.py:713-856`). Hard standard 3 is satisfied, although explicit fail-closed checks would be more robust than optimization-removable `assert` statements.
- Seed, paths, variant count, and zero-GPU use are explicit (`probes/047/run.py:62-101`, `probes/047/run.py:1161-1177`). No hidden model or test-set access was found.
- Readability is good: the module docstring states the experiment and status semantics, phases are narrated, provenance is attached to thresholds, progress is printed per case, and the run ends with a plain-language interpretation template (`probes/047/run.py:1-43`, `probes/047/run.py:1000-1243`).
- Practical smoke verification: `python3 probes/047/run.py --smoke --output-dir <new-temp-dir>` returned exit 0 in under one second, produced both determinism manifests with byte-identical content, and reported `status: SMOKE_ONLY`. The smoke path uses synthetic inputs, skips approval and real pins, and cannot emit either contractual Phase-A completion status (`probes/047/run.py:859-930`, `probes/047/run.py:1145-1155`), satisfying Hard standard 6.
- `requirements.txt` correctly declares standard-library-only execution. No interactive prompt or GPU dependency exists, and `--output-dir` controls the output location.

```json
{"verdict": "REVISE", "blocking": ["Hard standard 4: the default real run fetches the clinical dictionary over the network instead of requiring a pre-staged pinned input (run.py:220-227, 673-698).", "Hard standard 5: the pre-access split manifest contains anonymous row numbers rather than the frozen 99 case IDs, so its hash does not bind the split before the outcome-derived contribution table is opened (run.py:295-315, 389-432).", "Hard standard 1: the start/end determinism manifests omit the claim-bearing dictionary and the registered SUPPORT_PROVENANCE_FAILURE path returns without an end manifest or agreement check (run.py:1041-1053, 1068-1082, 1130-1142, 1208-1216)."], "note": "Scientific logic is contract-faithful and smoke passes, but offline input binding, a case-identified pre-access split freeze, and complete determinism finalization are required."}
```
