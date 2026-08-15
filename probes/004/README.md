# Probe 004 — contract v2: the 425-pair reconstruction-sensitivity floor study

`run.py` implements `ideas/004/probe_contract.yaml` (contract_version: 2),
which supersedes the executed v1 load probe (PASSED 2026-08-12; the v1
driver, README, and notebook are preserved in git history, and the v1 output
bundle remains in `results/`).

The study: run the frozen released v2 ClassFine checkpoint on 425 predeclared
geometry-matched same-acquisition reconstruction pairs of the CT-RATE
validation split, and report per-head (18) x per-stratum paired score-change
distributions (tier 1, label-free, primary) plus a descriptive per-head
delta-AUROC against the released report-derived labels (tier 2, secondary,
zero threshold language). Any magnitude profile is a valid descriptive
outcome; the deliverable is the measured baseline itself.

## Two-phase approval (mechanically enforced)

The driver recomputes the git blob of the contract and compares it to the
`contract_blob` recorded in `ideas/004/HUMAN_APPROVED_PROBE`. That single
check makes the contract's two-phase flow mechanical:

1. **Phase M — manifest freeze (authorized by the current phase-1 approval).**
   Metadata only: downloads at most the three pinned CSV tables, regenerates
   the frozen 425-pair manifest, hard-gates the per-stratum counts against
   237/126/58/4, and prints the two values the operator must record.
   No image download, no inference, no score of any kind.
2. **Operator amendment.** Record `pair_manifest_sha256` and
   `unique_volume_count` in the contract (replacing every
   `TO_BE_RECORDED_AT_MANIFEST_FREEZE` placeholder), commit, and re-run
   approve-probe. The amendment changes the contract blob, which stales the
   phase-1 marker by construction.
3. **Phase B — bulk study (requires the fresh phase-2 approval).** The driver
   refuses phase B while any placeholder remains or the marker blob does not
   match the amended contract. Then: chunked download → hash → preprocess →
   infer → delete over 17 chunks of 25 pairs, anchor drift-detector at every
   session start, preregistered spot-checks, and the frozen two-tier
   analysis once all chunks are complete.

## One command per phase

```
pip install -r probes/004/requirements.txt   # pinned r6 closure

python probes/004/run.py --smoke             # synthetic harness test:
                                             # no network, no GPU, no HF
                                             # gate (the hash-bound human-
                                             # approval gate DOES run).
                                             # Run it AFTER installing
                                             # requirements so the analysis
                                             # code is covered too.

python probes/004/run.py --phase M --output-dir <BUNDLE_DIR>
python probes/004/run.py --phase B --output-dir <BUNDLE_DIR>
```

`<BUNDLE_DIR>` is the results bundle (contract `results_bundle_layout`). On
Colab use a persistent Drive path: phase B is multi-session and resumes by
reading the bundle. One invocation of `--phase B` is one session (session cap
30); interrupted chunks are detected next session and redone in full. Phase B
always needs a GPU runtime — the anchor protocol runs at every session start,
including a final analysis-only session.

Session accounting is fail-closed: every `--phase B` invocation registers
itself in `<BUNDLE_DIR>/sessions/session_attempts.csv` at entry, before any
download, model, or anchor work. A session that crashes during setup still
counts against the cap of 30, and attempt 31 is refused before it begins.
Do not edit or delete that file; it is the R8 budget record.

Real runs additionally need the CT-RATE gate accepted on Hugging Face and a
logged-in HF token in the environment.

## Notes for the operator

- The anchor volumes are cached at `<BUNDLE_DIR>/../anchor_cache_004/`
  (SHA-256 verified before every use). Keep it on Drive to avoid re-download.
- The cross-session anchor check compares against the v1 reference scores in
  `probes/004/results/per_sample.csv`, pinned by git blob
  `ea1cdd3f...` in the contract. Do not modify or delete that file; it is
  load-bearing for phase B.
- `results_v2/` and smoke outputs are gitignored by default; commit the
  bundle (or at least `manifest/`, `analysis/`, `summary.json`,
  `provenance.json`, `anchor/`) with `git add -f` after human review.
- Exit codes are enumerated in the `run.py` module docstring; every one maps
  to a contract invalidating-failure class or an environment/harness fault.
  An invalidating failure is never a negative result.

## Verification status

See `verification.json`. This revision of the driver was written in a
sandbox that cannot execute Python, so verification there is static
(constants cross-checked against the approved contract by text search, plus
an independent code review). **The smoke run is therefore the first command
to execute — run it before phase M and read its `harness_checks`.**
