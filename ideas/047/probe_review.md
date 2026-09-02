# Probe code review — idea 047, contract v3, Phase B

## Verdict

**REVISE.** The Phase-B implementation is otherwise close to the approved
contract: it stages only the frozen 198 phenotype members, verifies archive
and member identity before parsing, implements the seven-variable closed
statistic menu and both approved exploratory displays, preserves the
phenotype-schema stop, and writes the contract's normal and reduced result
interfaces. One hard-standard ordering violation remains: the split manifest
is not frozen before outcome-derived inputs are opened.

## Blocking finding

### Hard standard 5 — split manifest is created after outcome-derived table access

`run()` hashes and then opens both the final-infarct-derived contribution
table and the consumed support table through `load_contributions()` and
`load_support()` before it calls `freeze_split()`
(`probes/047/run.py:1701-1720`). The split file is only written inside
`freeze_split()` (`probes/047/run.py:590-619`). Thus the statement embedded in
the emitted manifest—`created_before_any_phenotype_byte_staged`—is true but
weaker than hard standard 5, which requires the split manifest to be hashed
before **any outcome/label access**, not merely before this phase's phenotype
files are staged. The contribution and support tables are outcome-derived
claim-bearing inputs from the idea-023/046 lineage, so historical prior access
does not make the current execution order compliant.

This is fail-closed scientifically—the code cannot silently change the head
and still pass its later identity gates—but it fails the mandatory temporal
separation. Repair without expanding scope: bind and verify the already
produced Phase-A split artifact (or another exact predeclared 10/89 manifest),
materialize and hash it before opening either outcome-derived table, and only
then open those tables to verify exact ID/stratum agreement. The manifest must
state the stronger fact it actually enforces. The contract's dataset and
analysis need not change.

## Contract fidelity and silent-failure review

- The real path enforces a fresh approval binding the exact v3 blob and checks
  all contract literals (`probes/047/run.py:303-369`). It permits one variant,
  zero GPU minutes, and one fixed seed used only for 10,000 relabelings.
- Input hashes, the historical Phase-A governing blob, all seven frozen
  constants, and the dictionary-derived bindings fail closed before staging
  (`probes/047/run.py:394-578`, `probes/047/run.py:1701-1716`).
- Member discovery resolves exactly two phenotype files per analyzed case;
  archive bytes/MD5, extraction return code, staged-tree containment, member
  size, and CRC32 are all checked before parsing (`probes/047/run.py:648-800`).
- Empty files, duplicate normalized headers, multiple data rows, malformed
  values, missing fields, and insufficient head coverage surface explicitly
  in the schema census rather than becoming numeric values
  (`probes/047/run.py:808-1012`). The minimum-schema failure emits the
  contract's reduced interface and `PHENOTYPE_SCHEMA_MISMATCH`, explicitly not
  a negative (`probes/047/run.py:1870-1905`).
- The normal path implements only the closed continuous, ordinal, and binary
  summaries and contrasts. The signed 79.29% share remains separately labeled
  reversal accounting, and output language does not create a clinical,
  proportionality, causal, model-use, or generalization verdict
  (`probes/047/run.py:1045-1380`, `probes/047/run.py:1941-1998`).
- Every contract-required normal output is written. The schema-stop path emits
  exactly its documented reduced interface. Additional split, staging,
  exclusions, and determinism artifacts are provenance outputs, not added
  analyses.

## Standards checklist

1. **Start/end determinism manifests:** implemented over frozen inputs,
   consumed artifacts, the member manifest, staged-member aggregate, seed,
   mode, and row counts; equality is required on both registered terminal
   paths (`probes/047/run.py:1606-1632`, `probes/047/run.py:1701-1715`,
   `probes/047/run.py:1773-1829`, `probes/047/run.py:1891-1893`,
   `probes/047/run.py:1974-1978`). PASS.
2. **Exclusions log:** both lineage exclusions and every phenotype-file
   anomaly are emitted with reasons (`probes/047/run.py:1815-1822`). PASS.
3. **Assertion/check per transform:** parsing, joins, identities, staging,
   schema resolution, statistics, and output invariants carry explicit checks
   or assertions. PASS. Several internal invariants still use Python `assert`
   (`probes/047/run.py:465-466`, `probes/047/run.py:595-600`,
   `probes/047/run.py:1731-1732`); the documented command does not use
   optimization and surrounding pin checks cover the claim-bearing inputs, so
   this is non-blocking.
4. **Declared seed/paths and no network:** paths and seed are explicit; the
   real run requires local archive and manifest paths; imports and execution
   contain no analysis-time network operation. PASS.
5. **Split manifest before outcome/label access:** FAIL as detailed above.
6. **Smoke:** `python3 probes/047/run.py --smoke --output-dir <fresh-temp>`
   completed in under one second during review, emitted `SMOKE_ONLY`, exercised
   missing-field, parse-failure, file-anomaly, alternate-payload-spelling, and
   suppression paths, and produced byte-identical start/end manifests. It
   skips approval and cannot emit `STUDY_COMPLETE`. PASS.

## Practical verification and non-blocking findings

- `python3 -m py_compile probes/047/run.py` passed.
- Requirements are Python-standard-library-only; the real staging path names
  the external `7z` prerequisite and fails loudly if it is unavailable
  (`probes/047/requirements.txt`, `probes/047/run.py:728-755`). Output is
  confined to `--output-dir`, with no prompt or GPU dependency.
- Small-cell suppression is honestly limited: the code records that mandated
  margins and contrasts can arithmetically bound a suppressed cell
  (`probes/047/run.py:1369-1379`). This matches the approved cell-level rule
  and is surfaced for interpretation, so it is not a code-review blocker.

```json
{"verdict": "REVISE", "blocking": ["Hard standard 5: run.py opens the outcome-derived contribution and support tables before writing and hashing the 10/89 split manifest (run.py:1701-1720; freeze occurs at 590-619). Bind/materialize the predeclared split first, then verify those tables against it."], "note": "The scientific analysis and phenotype boundary are otherwise contract-faithful; one split-freeze ordering repair is required."}
```
