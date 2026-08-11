# Probe code review — idea 004 (load probe, contract v1) — ROUND 3

**Reviewed artifacts:** `probes/004/run.py` (1,086 lines, revision commit
ebe7e4a), `probes/004/requirements.txt`, `probes/004/README.md`,
`probes/004/verification.json`, and the contract sync in
`ideas/004/probe_contract.yaml`. Round-2 review (commit 657acc2) issued
REVISE with two blocking findings, R1 (broken in-process editable install /
missing import-time dependency pins) and R2 (environment failures misrouted
to contract exit 5). This round verifies the fixes.

**Review method.** Full read of the revised `run.py` and the
657acc2→ebe7e4a diff. Independently verified today (2026-08-12): the four
risky new pins exist on PyPI — `ema-pytorch==0.7.7`,
`vector-quantize-pytorch==1.1.2` (the API-sensitive one, pinned to the
released `setup.py` value), `beartype==0.19.0`, `torchvision==0.20.1` —
and PyPI metadata confirms `torchvision==0.20.1` requires exactly
`torch==2.5.1`, so the matched pair R1(c) demanded is correct. Re-confirmed
the CT-CLIP repository layout on GitHub: both `transformer_maskgit/` and
`CT_CLIP/` project roots contain `setup.py` with the importable package one
directory below, which is what the new `sys.path` strategy assumes (package
`__init__` chains were already verified from fetched sources in round 2).
I could not execute the smoke test in this review environment (code
execution is sandboxed off); the coder's committed `verification.json`
records a passing smoke run with all seven artifacts and the new
`execution_metrics` schema, and the smoke path was verified line-by-line
statically.

**Verdict: APPROVE.** Both round-2 blockers are fixed correctly, all four
round-2 non-blocking findings that could be fixed in code were addressed,
and the diff introduces no scope drift: still one pair, three executions,
one seed, same caps, same diagnostic-only framing of the A-vs-B difference.

---

## Round-2 blocker status

| # | Status | Evidence |
|---|---|---|
| R1 (import provisioning) | **FIXED, verified** | The in-process `pip install --no-deps -e` is gone. `run.py:781-790` inserts the two released project roots (`vendor/CT-CLIP/transformer_maskgit`, `vendor/CT-CLIP/CT_CLIP`) directly into `sys.path` — the round-2 review's own recommended alternative, effective immediately in-process, no `.pth` timing problem, no environment mutation. `requirements.txt` now pins the full verified import-time set: matched `torch==2.5.1`/`torchvision==0.20.1`, `vector-quantize-pytorch==1.1.2`, `ema-pytorch==0.7.7`, `einops==0.8.0`, `beartype==0.19.0`, `accelerate==0.33.0`, plus the `eval.py` chain (`h5py`, `matplotlib`, `seaborn`, `scipy`, `pillow`). README documents install as an explicit pre-step and states run.py never mutates its own environment. PHASE 1 fail-fasts to exit 11 on any unimportable dependency (`run.py:302-313`), so a provisioning gap can no longer masquerade as a contract result. |
| R2 (exit routing) | **FIXED, verified** | All three misrouting cases closed. CPU-only runtime: PHASE 1 now fails with exit 11 when `torch.cuda.is_available()` is false (`run.py:298-300`) instead of logging and continuing into `model.cuda()`. Tokenizer/text-encoder download: wrapped in its own handler routing to new environment exit 10 (`run.py:890-896`), documented in the docstring and README. torch/torchvision ABI mismatch: the PHASE 1 dependency loop now catches `Exception`, not just `ImportError` (`run.py:306-313`), so the `RuntimeError` from a mismatched `import torchvision` lands at exit 11 before PHASE 4 exists. Explicit `except SystemExit: raise` guards (`run.py:917, 955, 985`) keep the `fail()` exits from being swallowed by the broad handlers. |

## Round-2 non-blocking findings status

1. **Secondary metrics persisted — FIXED.** `run_three_executions` now
   threads per-execution metrics through to `summary.json` as
   `execution_metrics` (per-execution wall seconds; real mode adds
   `peak_gpu_memory_gb` per execution via
   `torch.cuda.reset_peak_memory_stats()` / `max_memory_allocated`,
   `run.py:972-980, 550-554, 1017`). The contract's secondary metrics are
   now in a required output, not just the log.
2. **`use_deterministic_algorithms` — FIXED.** Now
   `warn_only=True` (`run.py:295`) with the empirical repeat-A bit-identity
   check as arbiter, exactly the round-2 suggestion; a missing deterministic
   kernel can no longer crash mid-scoring into a false exit 9.
3. **Qualifying-pair count — FIXED (stronger than asked).** The count is now
   a hard gate: any deviation from Stage 0's directly inspected 237 stops
   the run (`run.py:836-839`) before the volumes are downloaded. See
   observation 1 below on the exit-code choice.
4. **Rerun clobbering — NOT ADDRESSED, carried.** `run.py:1064` still
   truncates `run_log.txt` and artifacts overwrite in place. Less salient
   now that R1(b)'s forced first-run failure is gone, but a rerun into a
   persistent Drive folder still silently replaces the previous attempt.
5. **Approval-flag discrepancy — RESOLVED (with a provenance note).**
   `probe_contract.yaml` now ends `human_approved: true`, synchronized in
   the same commit as the code revision rather than in a separate
   human-authored commit. The committed marker file
   `ideas/004/HUMAN_APPROVED_PROBE` (commit 3ecee0e, 2026-08-11) remains the
   human's actual approval act and the gate the code checks
   (`run.py:238-241`), and the sync changes no substantive contract field —
   caps, dataset, stopping rule, and failure list are byte-identical. The
   human should be aware the flag flip was performed by the coder as
   bookkeeping against their existing approval.
6. **Device-handle inconsistency — carried, trivial.** `torch.device("cuda")`
   at `run.py:878` alongside `.cuda()` calls elsewhere; harmless.

## New observations (non-blocking)

1. **Manifest drift routes to contract exit 7.** The new count gate fails
   with exit 7 (`invalidating_failures[4]`, pair validity) if the released
   metadata at the live-resolved revision no longer yields exactly 237
   qualifying pairs. Stopping is unambiguously correct — a drifted manifest
   voids the pair's Stage-0 certification, and the gate fires before any
   volume download — but the *cause* could be an upstream repo update rather
   than anything about the selected pair. If this exit ever fires, read the
   failure message before treating it as a contract-invalidating result; the
   message text does say "release contents or matching logic drifted".
2. **The pinned environment has not been install-tested end to end.** The
   coder's environment (like this reviewer's) cannot run pip, so the
   clean-venv `pip install -r` + import smoke test the round-2 fix asked for
   remains undone. Mitigations verified this round: every risky pin exists
   on PyPI, the torch/torchvision pair is exactly matched per PyPI metadata,
   and the key cross-constraints hold (`numpy==1.26.4` satisfies
   `scipy==1.14.1` and `accelerate==0.33.0`; `huggingface-hub==0.22.2`
   satisfies `transformers==4.38.2` and `accelerate`). A residual resolver
   conflict would fail loudly at `pip install`, before `run.py` starts, and
   any import gap fail-fasts at exit 11 — an inconvenience on first run, not
   a silent-failure surface and not a false contract result. Instruction to
   the human runner: run `pip install -r probes/004/requirements.txt` and
   let it finish cleanly before invoking the probe; report any resolver
   error as an environment finding, never as a probe result.

## Verified faithful this round (no action)

- The scoring call, checkpoint load (`weights_only=False`,
  `strict=True`), CTViT/CTCLIP constructor arguments, staging layout,
  4-tuple dataset unpack, head-order assertion against the released labels
  CSV, split guards on every download, provenance-before-inference ordering,
  contract-cap assertions in PHASE 0, bit-identity via raw byte comparison,
  and the smoke mode's planted-decoy self-tests are all unchanged from the
  round-2-verified state.
- Scope discipline held: the 657acc2→ebe7e4a diff touches only the two
  blockers, four of the six carried non-blocking findings, and their
  documentation. No new analysis, no extra executions, no contract-cap
  drift, and the interpretation strings still refuse any reconstruction-
  sensitivity reading of the A-vs-B diagnostic.

## Conditions of this approval

Approval covers exactly the committed revision (ebe7e4a) run under the
committed contract v1: three executions on one predeclared pair, 45-GPU-
minute cap, one seed. A passing real run authorizes only a *request* for
human approval of the separate 425-pair floor-study contract, per the
contract's positive_pattern. Any edit to `run.py` beyond the two carried
trivia (findings 4 and 6) should return for re-review.

```json
{"verdict": "APPROVE", "blocking": [], "note": "R1 fixed via sys.path insertion plus a complete, PyPI-verified pin set with matched torch 2.5.1/torchvision 0.20.1; R2 fixed via a phase-1 GPU gate, exit-10 tokenizer routing, and Exception-wide dependency checks — no new blocking findings, no scope drift."}
```
