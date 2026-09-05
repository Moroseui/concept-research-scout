# Fable review package and cleanup operation — approval pending

Implementation pin: **194cdcd** (M1 safeguards). Baseline: **4f5b6b1**.
Review the full diff and `scripts/rehearse_047_cleanup.py`, the publication
module, generated launcher, tests, dataset notice and this operation. Fable's
review is advisory; neither it nor this campaign ratifies 047 acceptance.

## Concrete proposed operation

Only `refs/heads/results/probe-047-dc586665d0be` contains the contaminated
source commit among all refs advertised by origin, including its advertised
pull-request ref. Verified using a separate blob-filtered mirror on 2026-09-05.
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
fact. A follow-up review is requested with this clarification.

Approving this cleanup will **not** make the 16-file tree importable. The present
policy still requires the exclusions audit and blocks 047. Removing/aggregating
that required audit interface needs an explicit separate ruling and a bound
policy/contract amendment. Successful-session console evidence and historical
registry attestation also remain open. No scientific acceptance is implied.
