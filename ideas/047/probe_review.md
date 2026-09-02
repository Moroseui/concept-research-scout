# Probe code review — idea 047, contract v3, Phase B

## Verdict

**APPROVE.** The prior hard-standard-5 blocker is repaired. The implementation
now materializes and hashes the predeclared 10/89 split before hashing or
opening either outcome-derived table, then fails closed unless both frozen
tables agree exactly with that declaration. I found no remaining contract,
silent-failure, claim-discipline, hard-standard, requirements, or Colab
practicality blocker.

## Resolution of the prior blocking finding

The complete 99-case rank ordering is now an authoring-time declaration in
`FROZEN_ANALYZED_IDS_BY_RANK` (`probes/047/run.py:151-195`). `run()` calls
`freeze_split()` before constructing, hashing, or opening the contribution and
support inputs (`probes/047/run.py:1765-1775`; the first hash/open occurs at
`probes/047/run.py:1813-1822`). `freeze_split()` writes `split_manifest.csv`,
hashes it, and records the stronger temporal claim
`created_before_any_outcome_derived_table_opened` (`probes/047/run.py:642-686`).
After the outcome-derived tables are opened, `verify_split_against_tables()`
requires exact rank-to-ID agreement and exact support-table head flags
(`probes/047/run.py:690-711`). Any mismatch exits as an input-identity failure;
the code never reselects a split. Hard standard 5 now passes.

## Contract fidelity and silent-failure review

- Fresh authority is bound to the exact current contract blob, and the code
  verifies the contract's version, limits, pins, variable spellings, terminal
  names, and output names before a real run (`probes/047/run.py:353-418`).
- The code implements one variant, zero GPU minutes, and one seed used only for
  the frozen 10,000 hypothetical relabelings (`probes/047/run.py:63-75`,
  `probes/047/run.py:1942-1946`). The primary output is the single seven-variable
  aggregate 10-versus-89 estimation table with the closed statistic menu and
  D4 support columns (`probes/047/run.py:1120-1402`,
  `probes/047/run.py:2014-2033`).
- Input handling is fail-closed: exact hashes and historical governing identity
  are checked before parsing; empty, malformed, duplicate, nonfinite, or
  identity-inconsistent contribution/support data cannot produce a result
  (`probes/047/run.py:428-599`).
- Staging is restricted to exactly two phenotype members for each declared
  case. Archive byte count/MD5, extraction return code, staged-tree contents,
  member size, and CRC32 are checked before clinical parsing
  (`probes/047/run.py:728-895`, `probes/047/run.py:1836-1886`). No network call
  exists in the probe.
- Header ambiguity, empty files, multiple rows, empty cells, and parse failures
  are counted explicitly rather than coerced into numeric results
  (`probes/047/run.py:897-1033`). Failure of the minimum schema emits the
  contract's reduced interface and `PHENOTYPE_SCHEMA_MISMATCH`, explicitly not
  a negative (`probes/047/run.py:1978-2012`).
- The normal path writes every v3 required output: `resolved_config.json`,
  `input_manifest.csv`, `staging_audit.json`,
  `phenotype_schema_census.csv`, `clinical_estimation_table.csv`,
  `clinical_uncertainty.json`, `suppression_log.csv`, `summary.json`,
  `environment.txt`, and `run_log.txt` (`probes/047/run.py:1867-1886`,
  `probes/047/run.py:1903-1938`, `probes/047/run.py:1942-1976`,
  `probes/047/run.py:2022-2033`, `probes/047/run.py:2054-2109`). The stage-task's
  generic `per_sample.csv` expectation is inapplicable because contract v3
  explicitly prohibits per-case clinical output and declares a phase-specific
  interface.
- Status and prose remain within the frozen claim discipline. `STUDY_COMPLETE`
  means successful descriptive completion regardless of direction; the final
  plain-language text prohibits clinical-silence, markedness, proportionality,
  causal, and generalization readings (`probes/047/run.py:2051-2107`).

## Standards checklist

1. **Start/end determinism manifests:** start is built from frozen inputs,
   staged-member aggregate, row counts, seed, and mode; the end is recomputed
   and equality is mandatory on both registered terminal paths
   (`probes/047/run.py:1606-1727`, `probes/047/run.py:2000-2002`,
   `probes/047/run.py:2084-2087`). PASS.
2. **Exclusions log with reasons:** both lineage bookkeeping exclusions and all
   phenotype-file anomalies are written with explicit reasons
   (`probes/047/run.py:1925-1932`). PASS.
3. **Assertion/check per transform:** contribution identities, support
   identities, split construction/agreement, member resolution/extraction,
   parsing, joins, statistics, suppression, and output determinism each have an
   assertion or fail-closed check. PASS.
4. **Declared seeds/paths; no hidden state or analysis-time network:** constants
   and local paths are explicit; the archive and manifest are CLI inputs; no
   networking library or runtime resolution is used. PASS.
5. **Split manifest before outcome/label access:** repaired as described above.
   PASS.
6. **Smoke under 60 seconds and unable to satisfy a gate:** reviewer execution
   of `python3 probes/047/run.py --smoke --output-dir <fresh-temp>` completed in
   under one second, exercised 24 synthetic phenotype members plus missing,
   parse-failure, alternate-spelling, anomaly, and suppression paths, emitted
   `SMOKE_ONLY`, and produced byte-identical start/end manifests. Smoke bypasses
   real approval with the explicit identity `SMOKE_NOT_APPROVAL_ELIGIBLE` and
   cannot emit `STUDY_COMPLETE` (`probes/047/run.py:397-400`,
   `probes/047/run.py:2036-2051`). PASS.

## Readability, requirements, and practicalities

The module docstring states the experiment, terminals, invocation, and exit
codes; numbered phase comments track contract order; thresholds carry
provenance comments; progress is flushed throughout; and both real and smoke
terminals end with bounded plain-English interpretation text. `py_compile`
passed. `requirements.txt` correctly declares standard-library-only Python and
names `7z` as the sole system prerequisite. Output is confined to the explicit
`--output-dir`, which must be fresh; there are no prompts. No
`ideas/047/contract_requirements.md` exists, so requirements-governed checks are
not applicable.

Non-blocking observation: several internal invariants use Python `assert`
(`probes/047/run.py:513-514`, `probes/047/run.py:643-657`,
`probes/047/run.py:1841-1842`). The documented invocation does not enable
optimization, and the same claim-bearing inputs are protected by hash,
membership, and constant gates. This does not block this approved run, though
explicit fail calls would be more robust to an accidental `python -O` launch.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The predeclared split is now frozen and hashed before outcome-derived table access, then verified exactly; all six hard standards and the Phase-B contract pass."}
```
