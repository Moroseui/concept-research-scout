# Probe 047 — keystone-ten support arithmetic and clinical profile

**Position (2026-09-02): Phase A complete and ratified; contract v3
(blob `dc586665d0be…`) human-approved; `run.py` in this directory now
implements Phase B, the sole executable phase.**

Phase A executed under contract v2 (blob
`b4887c05a21bfe870589b5d9982066943df679d5`) and is **of record**:
terminal `PHASE_A_COMPLETE_REQUIRES_AMENDMENT`, bundle imported at
`probes/047/results/results_v2` (commit `6037f24`), interpretation
cross-family reviewed (APPROVE) and ratified. The Phase-A bundle
validates under its own historical blob forever; nothing re-authorizes
Phase-A execution, and this code refuses to recompute Phase-A science —
it only re-verifies the consumed artifacts' identity. The Phase-A
implementation of record is preserved in git history (commit `e9f5f94`
and earlier); the approval marker `ideas/047/HUMAN_APPROVED_PROBE`
binds the current v3 contract blob exactly.

## Running Phase B

One command into a new, empty output directory. The probe performs **no
network access**; both heavy inputs are pre-staged local paths:

- `--archive-file` — the held `train.7z` from immutable Zenodo record
  16813698 (99,014,629,647 bytes, md5 `36ae28b9…`), byte-count- and
  md5-verified before extraction. Use local disk, not a FUSE mount
  (2026-08-25/26 lessons).
- `--member-manifest` — a local copy of the frozen archive member
  manifest (`path,size,crc`), byte-verified against git blob
  `edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2` before use. Materialize it
  from the repository with:

  ```bash
  git cat-file blob edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2 > archive_manifest.csv
  ```

The single real staging event uses the system `7z` binary (p7zip;
override the executable with `--sevenzip`); it is the only non-stdlib
dependency and only the real run needs it.

```bash
python probes/047/run.py --output-dir /path/to/probe-047-phase-b \
    --archive-file /path/to/train.7z \
    --member-manifest /path/to/archive_manifest.csv
```

Synthetic harness check (no archive, no 7z, no real inputs, never a
gate):

```bash
python probes/047/run.py --smoke --output-dir /tmp/probe-047-smoke
```

Exit codes: 0 valid completion (`STUDY_COMPLETE` or `SMOKE_ONLY`); 2
authority/CLI; 3 input identity (pin, blob, constant, or
archive-identity mismatch); 4 pre-registered `PHENOTYPE_SCHEMA_MISMATCH`
stop; 5 staging-integrity failure; 6 scope/blindness; 7
output/determinism; 8 wall time; 12 unexpected fault.

## What Phase B does, in contract order

1. **Split freeze (hard standard 5).** `split_manifest.csv` (99 case
   ids, head/rest strata) is materialized from the authoring-time
   declaration `FROZEN_ANALYZED_IDS_BY_RANK` — bound at code review
   from the pinned contribution table, never read from a file at run
   time — and is written and hashed BEFORE any outcome-derived table
   (contribution or support) is hashed or opened, before the archive
   is touched, and before any phenotype byte exists on disk.
2. **Identity gates (step 1).** SHA-256 pins on the three frozen inputs
   (`exclusions.csv` `58e9f8ab…`, `per_case_contributions.csv`
   `aba52512…`, `census_summary.json` `189c0ce8…`) and both consumed
   Phase-A artifacts (`proposed_variable_freeze.json` `87c5e11b…`,
   `per_case_support.csv` `994a4f88…`); the member manifest's git blob;
   the Phase-A bundle's own recorded governing blob; exact agreement of
   the loaded tables with the predeclared split (rank→id mapping and
   `in_head` flags; any disagreement is an invalidating input-identity
   failure); head-membership cross-check (the ten `in_head=True` rows
   must be exactly signed_rank 1–10); and exact recomputation of all
   seven frozen Phase-A constants (`math.fsum` is correctly rounded, so
   equality is exact). The bound variable list is also checked against
   the machine proposal's spellings.
3. **Staging (step 2).** The 198-member extraction set is resolved from
   the frozen manifest (tolerating the `sub-stroke`/`sub-strokecase`
   payload spellings by case-number canonicalization); archive byte
   count and md5 are verified; ONE selective `7z x` invocation extracts
   exactly those members; every staged file is size- and CRC32-verified
   against the manifest before any byte is parsed, and the staged tree
   is proven to contain nothing else. Everything is receipted in
   `staging_audit.json`. Staging transport is uncapped; the 15-minute
   post-staging analysis wall starts when it completes.
4. **Schema/missingness census (step 3).** Every staged member is
   parsed; each bound field resolves by the frozen normalization rule
   (trim, casefold, collapse whitespace; exact equality; expected file
   family preferred, either tolerated, never a different spelling).
   `phenotype_schema_census.csv` records per-variable, per-stratum
   counts only — no clinical value. Pre-registered stop: if the rows
   cannot support the minimum variable set (one of {MRS 3 months,
   NIHSS 24h, NIHSS at admission} AND one of {Age, Sex} with ≥1
   non-missing value each), the run stops as
   `PHENOTYPE_SCHEMA_MISMATCH` (exit 4) with the reduced interface —
   a decision-grade stop for escalation, not a negative.
5. **Estimation table (step 4).** The single aggregate 10-versus-89
   table over the seven bound variables with the closed statistic menu
   (continuous: mean/SD, median/IQR, SMD, difference in medians;
   ordinal: level counts, cumulative distribution, difference in
   medians, rank-biserial; binary: counts/proportions, difference in
   proportions of F), both frozen exploratory uncertainty displays per
   contrast (deterministic leave-one-head-case-out range; central 95%
   of 10,000 seed-20260902 relabelings under the verbatim label
   "hypothetical exchangeability reference; not a confidence interval;
   not sampling inference"), the D4 joint support display on every row
   (head/rest B_i medians plus the two frozen Phase-A shares), per-group
   missingness, and the frozen small-cell suppression (any ordinal or
   categorical level with 1–2 head cases displays `<3`; zero stays 0;
   every suppression logged, including the direct-difference guard on
   head cumulative cells and the derived head proportion). A bound
   variable that resolves nowhere is reported as a fully-missing row,
   never dropped.

## Blindness and scope

No perfusion map, NCCT, lesion mask, or any imaging member is staged or
read; a path guard refuses `.nii`, `perfusion-maps`, `lesion-msk`,
`_ncct`, and `per_patient.csv` outright. The 49 reserved cases and
`sub-stroke0043` are never touched (the extraction set is derived from
the 99 analyzed ids only, and the staged tree is walked to prove no
extra file exists). No per-case clinical value appears in any output;
`per_case_staging.csv` carries file bookkeeping only.

## What no outcome authorizes

Both terminal statuses are descriptive. The probe defines no separation
verdict, no clinically-silent or clinically-marked reading, no keystone
label, no proportionality verdict, no per-patient claim, no model-use or
causal claim, and no generalization beyond the realized 99 cases. The
signed 79.29% share is republished only as separately-labeled reversal
accounting; the relabeling ranges are never confidence intervals. An
absence of large separation may be stated only as "no separation larger
than the displayed exploratory ranges was observed at the achieved
precision."

## Expected sequence

Phase A ✓ → record-result ✓ → interpret + review ✓ → ratify ✓ →
amendment (contract v3) ✓ → fresh human approval ✓ → **Phase B
probe-build (this code) → cross-family review → Phase B run** →
record-result (expected destination `probes/047/results/results_v2-dc586665d0be` for the
pinned historical import) → interpret → ratify. The
`ideas/047/registry.yaml` two-node DAG is now proposed; historical
attestation and Phase-B acceptance remain pending. See
`docs/isles-pilot/047_LIFECYCLE.md`.
