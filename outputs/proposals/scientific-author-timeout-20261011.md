# Scientific author timeout ? candidate awaiting independent review

Operator direction: allow 1,800 seconds for each scientific author call. The patch uses that bound for run-specification and result-interpretation authors and retains the existing 60-second outer watchdog margin. Specification reviewers stay at 900 seconds and interpretation reviewers at 1,200 seconds; administrative/default bounds stay unchanged. No attempt, accounting, isolation, credential or failure-handling rule changes.

Candidate source: `7d9ed0c033caa7b5c0d1a9dc09c3c117e41b9841`. This safe projection preserves the changed tests. The full transport source is withheld because it contains infrastructure and credential-path references. Private evidence retains the exact source, operator authority, full diff, tests and review packet. Nothing here claims installation or scientific acceptance.

Validation: 101 tests pass; four fixture setup errors occur on both the candidate and unchanged baseline. The focused timeout/recovery subset passes all 28 tests. Original failures are preserved. The independent review also receives the current direction question about delivering Colab smoke and the saved-output analysis with minimal overhead.
