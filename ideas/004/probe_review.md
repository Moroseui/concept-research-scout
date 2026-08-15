# Probe code review — idea 004, contract v2, revision r1 (harness fault, exit 12)

**Verdict: APPROVE.** The revision implements exactly the two requirements of
the 2026-08-15 r1 revision spec (EXDEV-safe file relocation; full traceback in
the exit-12 handler) and nothing else. No scientific scope, endpoint, gate,
cap, or analysis line was touched.

## Scope of this review

The round-1 commit changes `probes/004/run.py` by three hunks (14 lines) and
rewrites `probes/004/verification.json`; `probe_contract.yaml`,
`contract_requirements.md`, `requirements.txt`, `README.md`, and the launcher
notebook are byte-identical to the previously approved state (verified by git
diff against the parent commit). The prior line-by-line contract and
requirements review therefore stands in full; this review re-examines the
diff, the failure class it repairs, and the fail-closed properties of the
changed path.

## Blocking findings

None.

## Resolution of the r1 revision spec

**Requirement 1 — EXDEV-safe relocation across the --output-dir/scratch
boundary.** `stage_volume` replaces `os.link` with `shutil.copyfile`
(`probes/004/run.py:1593`), with a docstring stating the constraint the code
cannot show: the staging tree is local scratch while the source may sit on the
Drive mount (`probes/004/run.py:1580-1587`). This is the production fault
site: attempt 3 died after anchor cache hits, and the anchor flow stages from
the Drive-side cache (`out_dir.parent / "anchor_cache_004"`,
`probes/004/run.py:1973`) into local scratch (`probes/004/run.py:2005`) —
`os.link` across that boundary raises exactly `OSError(18, Invalid
cross-device link)`. A file-wide sweep confirms the class is closed, not just
the instance: zero occurrences of `os.link`, `os.rename`, `os.replace`,
`Path.rename`, `Path.replace`, or `shutil.move` remain anywhere in `run.py`.
The only other relocation in the file, the anchor-cache write
(`probes/004/run.py:1991`), was already a byte copy; every result-bundle
artifact is written directly into the output directory (open/write, never
moved into place), which cannot raise EXDEV.

**Requirement 2 — exit-12 traceback.** `traceback` is imported at module top
(`probes/004/run.py:105`), and the unexpected-error handler now prints the
repr followed by `traceback.print_exc(file=sys.stderr)`
(`probes/004/run.py:3123-3129`). `SystemExit` is re-raised above it
(`probes/004/run.py:3118-3119`), so every contract-classified exit code
bypasses the handler unchanged; only genuine harness faults gain the
traceback.

## Scope containment and approval binding

The r1 spec's closing condition holds: the contract blob is untouched by this
commit, so the phase-2 approval marker remains bound and valid, and the frozen
manifest, budgets, tiers, anchor protocol, and invalidating-failure taxonomy
are all unmodified. The diff adds no analysis, no threshold language, no new
output, and no data contact.

## Fail-closed audit of the changed path

- **No stale-copy hazard from the `if not link.exists()` guard.** A byte copy,
  unlike a hard link, is not atomic, so a copy killed mid-write could leave a
  partial staging file. Both call sites preclude reuse: the anchor staging
  tree is rmtree'd and recreated before staging (`probes/004/run.py:2000-2003`)
  and the chunk download/staging trees likewise at chunk start
  (`probes/004/run.py:2083-2086`), so the guard never sees remains of a prior
  attempt.
- **Copy failures fail loudly.** `shutil.copyfile` raises on I/O error (disk
  full, permission), which now lands in the exit-12 handler with a full
  traceback — the exact diagnosability the spec demanded.
- **Staged copies are not re-hashed, and that is acceptable.** The SHA-256 in
  the chunk manifest is computed on the downloaded source; with a hard link
  the staged file was the same inode, whereas a copy could in principle
  diverge. The failure direction remains a crash, not a silent number: volumes
  are `.nii.gz`, so a corrupted copy fails the gzip CRC at decode, and the
  anchor bit-identity and cross-session tolerance checks bound the residual
  risk on the anchor path.

## Non-blocking findings

1. **Transient disk per chunk roughly doubles.** Staging previously cost
   nothing (hard links); it now duplicates each volume's bytes until the
   end-of-chunk cleanup (`probes/004/run.py:2205-2206`), so a 25-pair chunk
   transiently holds ~50 GB (downloads plus staged copies) against the
   contract's "~25 GB transient disk" sizing note. Still comfortably inside
   Colab Pro+ local scratch, and R8 caps are volumes and sessions, not bytes,
   so no contract number is violated — but the operator should know the
   sizing rationale in R7 is now stale by a factor of two.
2. **The smoke harness does not exercise `stage_volume`.** The functional
   verification of the copy (byte equality, source retention) was performed
   ad hoc by the probe_code stage, not as a repeatable smoke check. Adding
   one would exceed the r1 spec's "ONLY these" scope; it belongs on the same
   run.py polish list as the naive placeholder scan (2026-08-15 amendment 2),
   not in a revision.
3. **One `verification.json` label overstates slightly.**
   `cross_filesystem_safe_staging_copy: passed` reflects a temp-dir copy test
   plus static greps; a true Drive↔scratch crossing is only exercisable in
   production. The substance verified is correct (stdlib byte copy has no
   rename semantics), so this is a labeling note only.

## Verification performed in this review

Python execution is unavailable in this review sandbox, so compile and smoke
were not re-run here. Statically verified: the full three-hunk diff against
the previously approved blob; the file-wide absence of bare link/rename
relocation calls; handler and import placement. Independently inspected the
probe_code stage's logged verification (`ideas/004/log_probe_code.txt`,
executed commands and outputs at lines 4597-4757): a real `--smoke` run
passed every harness check including the phase-B refusals and session-cap
fail-closed test; the `stage_volume` functional copy test passed; the static
asserts (no `os.link`/`.rename(`/`os.rename(`, traceback handler present)
passed; `ast.parse` of the source succeeded. The NumPy-backed analysis
portion was again skipped in that environment (`skipped_no_numpy`); this
remains non-blocking because NumPy is pinned in
`probes/004/requirements.txt:5` and the README requires a full smoke rerun
under the pinned requirements before any real phase.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The r1 diff is exactly the two authorized harness repairs (EXDEV-safe staging copy, exit-12 traceback), the relocation class is closed file-wide, and no scientific scope changed."}
```
