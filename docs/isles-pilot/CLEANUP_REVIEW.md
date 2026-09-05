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
`/tmp/isles-pilot-private/rehearsal-047-v2/rehearsal.git`:

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

Original evidence is retained, with owner-only access, OUTSIDE this checkout:
`/tmp/isles-pilot-private/rehearsal-047-v2/original-047.bundle` (verified by
`git bundle verify`), `probe_exclusions.original.csv`, and
`failure.original.console.log`. The bundle preserves original source and parent
bytes and ancestry; hashes alone are not the backup. The private receipt records
hashes and verification. Preserve this directory across cleanup; /tmp is not a
permanent archival service, so approval should include a durable private backup
location or retaining this machine until that copy is made.

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
