# RC3 deployment plan ? preparation only

Actual operator decision:

> Decision on item 7: option (b), a small new-lane deploy script, as the review describes. It replaces "existing installer" as the recorded interim choice; the legacy installer is not used or modified.

The user approves RC2 source9bf4d8e via001-claude-rc2-review.md and selects
**option(b), a small new-lane deploy script**. This supersedes the prior interim
choice of the legacy installer. `install_reviewed_deployment.py` is neither used
nor modified. Original RC2 approval and the older choice remain in their preserved
originals. No server deployment or model call occurs in this round.

Tag `research-manual-sprint10-20260926-rc3` and its commit/tag-object hashes are
bound in the review folder SOURCE.json. One manual review of this diff is pending.

## Fixed new layout and service templates

- Source: `/opt/research-system/manual-sprint10/rc3` (read-only, exact Git archive).
- New state: `/var/lib/research-system-manual-sprint10`, including empty repository,
  lane, workspaces and inbox directories, initially owned bypartho on the server.
- New configuration: `/etc/research-system/manual-sprint10` (partho-readable private
  directory; actual runtime mapping/logins are provisioned later with the user).
- Deployment evidence: `/var/lib/research-system-manual-sprint10-deployment/rc3`.
- Units: `research-manual-sprint10-rc3.service` and `.timer`, supplied verbatim from
  `deploy/manual-lane/`. Installed disabled/inactive, without enable links. The
  installer runs no daemon-reload, enable, stop or start operation. Old units must
  already be held by the separately authorized operator procedure below.

The service advances one driver transition, aspartho, and never initializes state.
The timer is disabled by installation. Before later enabling it, verify its actual
host restrictions, paths, credentials and runtime as the service account. The
working scientific repository must be an independent clone at the approved pin
on an `astra/manual-...` branch, not a worktree sharing the old canonical owner.
The installer intentionally creates it empty: clone/init and runtime/config/login
checks are separate held-provisioning steps, not hidden model launches.

## Required order before future live use

1. Record genuine RC3 review approval and exact source/tag/configuration identities.
   Reconcile active old jobs/calls and receipts; recover results before retries.
2. Take and verify the private old-state snapshot **before** stopping anything:
   job/accounting DBs with native consistent SQLite backup; receipts; logs;
   paused/control state; exact source and unit definitions and enabled/active
   states. Restore privately, verify integrity, row identities and file hashes.
   Save the completion receipt. This script verifies that receipt's supplied hash
   and PASS status; it does **not** perform or claim the operator's snapshot.
3. Record the original old-unit inventory. Then, under the existing user decision,
   stop/disable the listedc703d89 broker/timers and other old units. Do not delete,
   unpause, reset or migrate any old state. Preserve independent Colab notebooks.
   Inventory fields and the scratch example are in the review folder. A unit's
   definition hash is from `systemctl cat`; the original enabled/active states are
   retained for rollback, while installation requires current held states.
4. Run `tools/deploy_manual_lane.py install` with exact tag, reviewed commit,
   tag-object ID, original independent report/hash and recorded old inventory.
   Supply `--root / --live` only on the server asroot. Defaults never silently pick
   the live root. Every new destination must be absent, including unit files.
   No overwrites, repair-on-retry, old-path writes or legacy installer calls.
   Partial installation is preserved and requires reconciliation, not a rerun.
5. Require installed.json PASS. Source hashes originate from the pinned Git
   archive, not from self-hashing a possibly bad installed copy. Source and units
   are read back against that inventory. FILES.json also binds the old-state
   contract, review and generated rollback. Preserve the manifest hash externally.
6. Provision actual runtime.json using absolute package paths outside homes and
   private trees. Test both full runners and live denial probes on the server;
   laptop results do not establish that server evidence. Follow MANUAL_LOGIN.md
   for the exact user-present Codex and Claude setup-token commands. No API billing
   is enabled. All context, scanner, scientific authority and halt gates remain.
7. Rehearse the generated rollback with `rollback.sh --rehearsal` **once before any Sprint10 model call**, capture
   the completed receipt, then hold the old units again under the recorded decision.
   Do not silently rerun a partial rollback. A completed rollback replay verifies
   the saved outcome without repeating control operations. Rehearsal and post-run
   rollback have separate immutable intent/result records, so rehearsal does not
   consume the later rollback. The same pinned script handles both; no database
   is restored over work.
8. Prepare the independent writable repository/lane using `init --server-rerun`,
   reviewed source/report and the dedicated credentials. Only after held provisioning,
   snapshot/rehearsal, host validation, applicable audit and recorded conditional
   release gates pass may the new timer be enabled for this six-call lane.
9. The new run emits a fresh notebook package, followed by one operator Colab CPU
   run, collect/validation, interpretation/review and STATE/report. Do not relabel
   the old ZIP or rerun task921/d9 eligibility. Use the same99 development boundary,
   seven reference hashes, exact nonnumeric checks and predeclared numeric tolerance
   (absolute1e-10/relative1e-9, fixed bootstrap seed0). No training or locked cases.

## Rollback and precise preservation contract

After a successful install, the one command is:

```sh
sudo /var/lib/research-system-manual-sprint10-deployment/rc3/rollback.sh
```

It binds the installed implementation and recorded old-unit inventory. It checks
installed hashes and old-state invariants, stops/disables only the new units,
then re-enables/starts exactly the old states recorded before their hold. New
state/results are retained in place; no files or databases are deleted/restored.

The unchanged-old-state check covers exact pause/control bytes (including revision),
SQLite schema and logical row content, and the complete receipt-file inventory.
Logs may grow: each original log prefix must remain byte-identical and untruncated.
New/changed receipts or database rows still fail even if caused by an old service's
restart. Such failure is preserved as RECONCILE_REQUIRED; it is never waived as
harmless log growth. Installed source/unit drift also blocks rollback. Old source,
configuration and data are never edited by this script; enabling/starting recorded
old units occurs only in explicit rollback, not installation.

The scratch test uses a simulated systemd backend under its scratch root, with
real Git export/hashing, SQLite rows, pause/receipt files and an executable generated
rollback. It proves file/state behavior, not real server systemd/auth behavior.
The actual RC3 candidate is also exported and rolled back in a laptop scratch root
using explicitly synthetic review evidence, never represented as a genuine approval.

## Call budget and later work

There are six total calls: spec author/review, interpretation author/review, and
one normal author/reviewer science revision if needed. A deterministic sentence-
boundary summary relocation is recorded in provenance and uses zero model calls.
The reviewer must still find the answer and main caveat in the shortened summary.
Original outputs/native receipts are preserved. No retry of failed/uncertain calls.

Sustained H2/scheduling/recovery acceptance and disconnected observation remain
later requirements. This known-case rerun remains distinct from new research and
still needs the operator's Colab run. RC3 prep does not claim laptop independence.
