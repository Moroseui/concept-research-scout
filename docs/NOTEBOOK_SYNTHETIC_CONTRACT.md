# Synthetic test interface for the revised 13B notebook

These are engineering checks, not patient computation or scientific acceptance.
The independent reviewer must inspect the real call sites and confirm that the
tested helpers govern the notebook's real behavior, rather than unused stubs.

- Cell 22: expose and use validate_full_folds(table, held), where table is a
  pandas DataFrame with case, fold, shuffle. Validate exactly five folds 0?4,
  99 unique development members, shuffle 101, exact one-to-one row membership,
  and no duplicates, missing or extra members or wrong fold assignments.
  Return normally for valid input; ValueError/AssertionError for invalid input.
  The real expected membership must be independently pinned; never derive the
  required full cohort from editable FOLDS_TO_RUN or observed table rows.
- Cell 22: expose and use verdict_from_intervals(base_ci, repeat_ci,
  complete=True). Each CI is (estimate, lower, upper). Return better only
  when both lower bounds are positive; worse only when both upper bounds are
  negative; otherwise no clear difference. Return provisional when incomplete.
  Refuse malformed, reversed or nonfinite intervals. No ratio/noise estimator.
  Preserve multiplicity and patient-resampling limitations in reporting.
- Cell 8: expose and use coverage_support(values, brain, coverage=None),
  returning (boolean support, metadata with coverage_known). With a supplied
  spatial coverage mask, support is brain AND coverage AND finite(values).
  Without it, return finite brain support and coverage_known=False, never
  infer anatomical coverage from all-zero maps. Keep valid zeros.
  The actual notebook must declare its coverage source/provenance or hold the
  affected execution pending that evidence; synthetic tests do not supply it.
- Cell 8: zscore_in_brain and histeq_in_brain operate only on supplied valid
  support, leave outside support zero, and return finite fallback output for
  empty/constant support. z-score metadata carries sd_used with the configured
  ZSCORE_MIN_SD floor.
- Cell 6: retain and run the notebook's six existing _fx lesion-metric checks.
  Do not alter their expected semantics to make tests pass.

The trusted harness extracts definitions from these actual cells. It does not
run cell top-level statements. It executes in a credential-free,
network-disabled CPU namespace with no source scans, caches, Drive, cohort
manifest, exclusions file or host home mounted. Synthetic IDs are
SYNTHETIC_000 etc.; synthetic arrays are created in memory.

The patch author supplies code, not a claimed test pass. The controller records
compile results, sandbox proof, harness hash, notebook hash, exit status and the
four test groups. All resulting evidence and the actual safe diff reach the
reviewer. Any real finding remains a finding. Item4's smoke and real-data
provenance remain unfulfilled execution conditions; this stage cannot waive them.

## Downstream evidence delivery

The interpretation and next-decision originals, like the notebook copy, diff and synthetic results, are delivered as hash-checked read-only workspace files. The reviewer must read the selected originals. Their complete scientific content is preserved without repeating it in the initial input. Public/privacy scanning and the 200,000-character input cap remain unchanged.
