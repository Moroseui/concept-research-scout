# Fable review package and cleanup operation — approval pending

Current reconciliation: [2026-09-06 receipt](CLEANUP_RECONCILIATION_20260906.json).
The fresh local rehearsal reproduced the exact replacement below, verified
original evidence bytes and traversed all 12 currently advertised refs. Historical
Fable approval at `469d29df002ea78f64146731244769d7c82330d6` remains advisory;
this stabilization adds a fresh integration review. Neither review grants cleanup
permission or ratifies 047 science. Main is still `4f5b6b1`.

## Concrete proposed operation

Only `refs/heads/results/probe-047-dc586665d0be` contains the contaminated
source commit among all refs advertised by origin, including the advertised
pull-request refs inspected. Verified using a fresh blob-filtered metadata
repository on 2026-09-06.
Remote main remains **4f5b6b1dc67084a7882c099fb30a6f9465991a31**.

- Before: **940293b6d562f2d3dd6bfd9d8d8281ccf01e4783**.
- After, rehearsed: **c812421207b6ddcba6516444897c777d8440275a**.
- Unchanged parent: **b652005fbcf6a87765a85e81b381a8596b4384ce**.
- Contract unchanged: **dc586665d0bece940d1a1f4b3b0572f8c951c2ba**.

Run only after explicit operator approval, from the disposable rehearsal repo
`/home/partho/concept-research-scout-v4/isles-pilot-private-evidence/rehearsal-047-v2/rehearsal.git`:

```bash
git push --force-with-lease=refs/heads/results/probe-047-dc586665d0be:940293b6d562f2d3dd6bfd9d8d8281ccf01e4783 https://github.com/Moroseui/concept-research-scout.git c812421207b6ddcba6516444897c777d8440275a:refs/heads/results/probe-047-dc586665d0be
```

No other ref, branch deletion, visibility change or main update is proposed.
A changed remote pin invalidates this operation and requires a fresh audit.
The lease is mandatory. The command has **not** been executed.

## Scope and evidence

The replay removes 198 staged raw phenotype files and quarantines the original
`probe_exclusions.csv` (four rows, three identities) privately. It retains the
other **16 top-level scientific/audit files byte-for-byte**. The original failure
console from the parent is also deposited at
`probes/047/results_v2.failure.console.log`, byte-for-byte; its parent-history
copy remains unchanged. No original successful console was found in Git or
local Downloads. `run_log.txt` is not a substitute. The failure console is not
misrepresented as successful-session evidence.

Original evidence is retained durably with owner-only access OUTSIDE this checkout:
`/home/partho/concept-research-scout-v4/isles-pilot-private-evidence/rehearsal-047-v2/`.
It contains `original-047.bundle`, `probe_exclusions.original.csv`,
`failure.original.console.log`, the disposable Git repository and verification
receipt. The durable copy passed `git bundle verify`: complete original history,
not merely hashes. A temporary copy remains under `/tmp/isles-pilot-private/`.
The separately preserved remote-ref inventory records the inspected upstream state.
No operator backup-location decision is now needed; cleanup approval alone remains
reserved. Revalidate these files and remote pins immediately before any update.

The rehearsal proved: exact parent retained, all 16 retained result blobs
identical, original failure bytes preserved, and exactly the intended paths
changed. A first rehearsal failed on bare-index worktree configuration before
creating a replacement commit; its evidence remains privately, and the corrected
second rehearsal succeeded. The optional full mirror was stopped because it
would download unrelated historical binary payloads; ref ancestry was instead
verified with a 712-KB blob-filtered mirror. The complete 047 evidence bundle
was independently verified and is unaffected by that change.

## Decisions still open

Quarantine is a publication disposition, **not scientific acceptance** and not
permission to exclude a required audit output. The exclusions file records
pre-existing bookkeeping exclusions plus two malformed phenotype-file records
for one case. Whether those records disclose prohibited per-patient clinical
information, and what aggregate replacement preserves their scientific meaning,
needs an explicit ruling. Until then 047 exports/import acceptance remain blocked.
No required output has been silently removed to pass validation.

The cleaned commit has a new source identity. Future import receipts must bind
that actual source and an explicit original-to-subset disposition manifest;
existing citations to 940293b6 remain historical citations and must not be
silently replaced. Phase A and all existing scientific records stay untouched.

A forced ref update cannot remove already downloaded clones, forks, cached
commit views, hidden service refs, or copied evidence. No claim of universal
erasure is possible. After approval and the leased update, re-query refs,
verify the new tree and request host-side cache handling separately if needed.

Supplemental reachability audit: all **11 advertised refs** were traversed with
lazy blob fetching disabled. The 198 raw files correspond to **173 distinct
Git blobs**; only the named 047 results branch reaches any of those blobs.
This checks blob reachability even without direct descent from the source commit.
The audit is preserved beside the durable private evidence. Hidden/unadvertised
service refs and copies remain outside what this check can establish.

## Independent review and clarified projection (continuation)

Claude Fable reviewed baseline 4f5b6b1..495269bc and returned APPROVE for the
cleanup operation, with no blocking findings. Actual review and CLI model/usage
receipts are under `reviews/cleanup-r1.*`; this is an agent review, not operator
approval. The CLI also reports a Haiku auxiliary call; Fable authored the review.
CLI dollar estimates are not evidence of a new charge on the subscription.

Following its recommendations, integrity checks now survive `python -O`, and the
rehearsal explicitly compares the exact OLD→NEW path-change set. A synthetic
rehearsal test passes and an optimized real rehearsal reproduces the SAME
c812421207b6ddcba6516444897c777d8440275a replacement with identical retained bytes.

**This projection removes raw phenotype payloads; it does not anonymize the
retained audit artifacts.** Local top-level metadata inspection confirms case
identifiers remain in `per_case_staging.csv`, `split_manifest.csv`, and
`staging_audit.json`. The per-case staging columns retain identity-linked file
usability/anomaly metadata. Quarantining `probe_exclusions.csv` therefore does
not remove all identity-linked anomaly information. The safe exported schema/count
audit is `reviews/047-retained-metadata-audit.json`; no patient values or IDs are
reproduced there. Fable's initial unverified suggestion that only staged inputs
and the exclusions file carry identities must not be treated as an established
fact. Claude Fable follow-up r2 at 3f0337b explicitly reviewed this clarification
and returned APPROVE for operator consideration, with no blockers. Original
response and execution/source manifest are preserved under reviews/cleanup-r2.*.

Approving this cleanup will **not** make the 16-file tree importable. The present
policy still requires the exclusions audit and blocks 047. Removing/aggregating
that required audit interface needs an explicit separate ruling and a bound
policy/contract amendment. Successful-session console evidence and historical
registry attestation also remain open. No scientific acceptance is implied.

Cleanup r4 and P001 r3 both returned actual APPROVE at the final reviewed
implementation pin above. These verdicts and their exact source manifests are
in reviews/. The proposed remote operation remains unchanged and unexecuted.

## Current proposed metadata disposition

| Artifact group | Proposed operation | Scientific acceptance consequence |
|---|---|---|
| 198 staged phenotype CSVs | Remove from replacement commit; complete originals remain in private bundle | Confirmed aggregate-only project publication-boundary violation; not needed as public outputs. |
| `probe_exclusions.csv` | Quarantine exact original privately | Required audit remains unresolved; removing it does not satisfy import policy. |
| `per_case_staging.csv`, `split_manifest.csv`, `staging_audit.json` | Retain exact bytes in this narrow operation, including case-linked usability/anomaly/stratum metadata | Explicit residual exposure; propose no new public copies or scientific acceptance until an operator disposition rules whether to retain or aggregate in a separate reviewed amendment/rehearsal. |
| Other 13 top-level files | Retain exact bytes | Aggregates/audit evidence preserved, not newly accepted. |
| Original failure console | Preserve parent history and add identical sibling file | Failure evidence only; missing successful console remains missing. |

This is deliberately a **raw-payload cleanup**, not anonymization. Approval of the
exact operation means accepting these residual public audit files for this narrow
step; a broader metadata cleanup requires a different exact projection and fresh
rehearsal. Frozen prior Phase-A and earlier scientific case-level records are not
removed. No blanket case-data erasure is claimed.

The confirmed issue is the project's aggregate-only publication boundary.
A separate licensing violation has not been established. The pinned
[Zenodo release](https://zenodo.org/records/16813698) and
[dataset notice](DATASET_NOTICE.md) remain the attribution references; the license
does not categorically ban redistribution. No overall repository license change
is proposed.

Fresh original bundle verification, exact path-change verification, 16 retained
blob comparisons and separately stored exclusions/failure-byte comparisons passed.
Fresh private evidence also exists at
`/home/partho/concept-research-scout-v4/isles-pilot-private-evidence/stabilization-20260906-r2/rehearsal`.
The prior approved operation may still be run from the original rehearsal repo
specified above; both reproduce the same after pin. The first refresh attempt
stopped because ordinary rev-list rejects intentionally omitted blobs. The second
explicitly allowed missing blob reporting and separately required complete
commit/tree traversal; it succeeded without downloading raw payloads. Its first
partial metadata repository is retained privately, not represented as successful.

Immediately before an approved push, repeat the affected-ref audit and bundle
verification and require the exact before pin. Afterward verify remote branch/tree,
retained bytes and unchanged unrelated refs. The new cleaned source identity must
be used in future provenance declarations; old citations remain historical.
Cached views, hidden refs, forks and copies need separate host/operator handling.
