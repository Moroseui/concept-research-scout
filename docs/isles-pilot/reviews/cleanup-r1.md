## Review verdict: APPROVE (cleanup scope) — the leased rewrite is technically suitable for operator approval, with no blocking findings

The proposed operation is sound: it is a single-ref, expected-value leased force push (`--force-with-lease=<ref>:940293b6…`), pinned to the exact remote state, replacing the contaminated commit with a deterministic sibling commit (`c8124212…`, same parent `b652005f…`, fixed author/date/message, so the hash is reproducible). The rehearsal script builds the new tree by `read-tree` from the original commit and removes only the 198 `staged/` files plus `probe_exclusions.csv`, so the arithmetic checks out (215 tracked files = 17 top-level + 198 staged; 16 retained = 17 − 1 quarantined), retained blobs are verified identical, the parent is unchanged, and the exit-7 failure console is deposited byte-for-byte without being relabeled as success evidence. Originals (full bundle, exclusions CSV, failure console, receipt) are preserved privately outside the checkout. Publication safeguards are fail-closed throughout: the 047 policy is `blocked`, the subset verifier refuses any non-`staged/` exclusion, the launcher no longer carries a write token or auto-pushes, and no code path in the revision can execute the push itself. The documentation correctly frames cleanup as a publication disposition, not scientific acceptance, and makes no universal-erasure claim.

### Non-blocking findings

1. **Medium — `scripts/rehearse_047_cleanup.py:main`: all integrity guarantees are `assert` statements.** Running under `python -O` strips every check (retained-byte identity, parent identity, counts, failure-console bytes) while still producing a replacement commit. Failure mechanism: a future re-rehearsal under optimization silently yields an unverified commit. Fix: replace `assert` with explicit `raise SystemExit(...)`; test by executing the module with `-O` against a synthetic repo and asserting refusals still fire.

2. **Medium — same file: "exactly the intended paths changed" is true by construction but never asserted, and the script has zero test coverage.** The first rehearsal's bare-repo worktree failure shows this script class is fragile. Fix: add a `git diff-tree -r --name-status OLD NEW` assertion that the change set equals exactly 198 `staged/` deletions + the exclusions-file deletion + one addition; parameterize the pinned constants and add a synthetic-repo test in the style of `tests/test_pilot_publication_audit.py`.

3. **Medium — `docs/isles-pilot/CHECKPOINT.json`: the recorded tip (`68298a87…`) and audit manifest do not cover the actually reviewed revision `495269bc…`.** The contaminated-ancestry and per-artifact checks attest an earlier tip; commits after `68298a87` are unaudited by the recorded receipt. This does not affect the cleanup ref operation (its pins are independent of the branch tip), but re-run `scripts/check_pilot_publication.py --tip 495269bc…` and refresh the checkpoint before any further branch push.

4. **Low — `scout.py:record_result`: one `publication.json` per probe binds a single `contract_blob`, but 047's registry has two contract pins.** Any future Phase-A-pinned import (`b4887c05…`) refuses with "publication policy contract mismatch" regardless of the `blocked` ruling. Fail-closed, so acceptable now; a contract-to-policy mapping will be needed. Test: synthetic import under a second pinned contract.

5. **Low — structural consequence worth stating explicitly: after the rewrite, no import path exists for the cleaned bundle.** Verbatim import fails the policy's `required` set (`probe_exclusions.csv` absent), and `publication_subset.verify` refuses non-`staged/` exclusions by design. Approving the cleanup therefore does not unlock 047; a separate operator ruling on the exclusions audit plus a policy/contract amendment (a new source-identity-bound subset or amended interface) is required first. This matches the stated intent — recorded here so it is not mistaken for an oversight.

6. **Low — `scripts/check_pilot_publication.py:audit`: the prefix/extension heuristics would mechanically pass a renamed raw text file** (e.g., `docs/isles-pilot/x.txt` under 1.5 MB); raw-artifact detection keys only on `/results/`, `/staged/`, `.private/`. Keep human review as the second gate or add content heuristics.

7. **Low — `orchestrator/campaign.py:verify_decision`: the human-approval forgery check covers only two key spellings** (`human_approved`, `approved_by_human`) in an open schema; a decision carrying e.g. `operator_approved: true` passes. Fix: closed key schema or reject any truthy key matching approval/ratification patterns, with a test. Also, the opposing-family review binds spec and code hashes but not the decision document itself, so a review could be replayed against a different decision under the same spec.

8. **Low — new orchestrator modules regress on the repo's bounded-git doctrine:** `publication.py` and `publication_subset.py` use `subprocess.check_output` without timeouts (unlike `scout.py:_git`), and a policy missing `allowed`/`required` raises `KeyError`, which `record_result` does not catch (still refuses, but via traceback). `publication.check_git_paths` appears unreferenced by any caller or test — remove or wire it in to prevent drift.

9. **Info** — the replacement commit will carry the fixed identity "scout cleanup rehearsal / 2026-09-05T12:00:00Z" on the public results branch. This is what makes the hash deterministic; noted so the authorship is not a surprise post-push.

### Unverified matters (out of supplied material or unexecutable here)

- Roughly half the inventory was not supplied in the diff (P001 `run.py`/`validate_return.py`/notebooks, `probes/047/run.py` change, the generated 047 notebook, `ideas/047/state.json`/`CARD.md`, `efficiency_review.py`, `package_pilot.py`, `README.md`, several tests) and is not covered by this review.
- With execution disabled I could not reproduce: the deterministic hash `c8124212…`, the rehearsal receipt, bundle verification, the 11-ref/173-blob reachability audit, the claim that the replacement (including parent history) reaches zero raw phenotype blobs, the checkpoint manifest SHA, or the 220/226/227 test counts. All are taken from the supplied documents.
- Content-level privacy of the 16 retained files (e.g., `per_case_staging.csv`, `per_case_support.csv`) rests on the prior audit that only `staged/` and `probe_exclusions.csv` carry identities; not verifiable from supplied material.
- Whether commit `495269bc…` contains exactly these bytes could not be confirmed without repository access.
- Colab execution/retrieval remains unverified, as the checkpoint itself states.

Cleanup approval remains distinct from scientific acceptance: the three open operator decisions (Phase-A registry attestation, exclusions-audit disposition, successful-console recovery) are correctly left open by this revision and are not resolved by this review.

```json
{"verdict": "APPROVE", "scope": "cleanup", "reviewed_commit": "495269bc6f72687f39d8c62ec9e2eb73162c390f", "blocking_findings": []}
```
