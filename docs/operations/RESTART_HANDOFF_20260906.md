# Hibernation checkpoint — 6 September 2026

Operator requested a safe pause. Do not resume agent work until the operator returns.
Branch: `astra/infrastructure-milestone-record`. Implementation HEAD before this
record: `b670743d33a351944887b2ee8ab0d75af4fcd626`. This document's containing commit
is the restart checkpoint; resolve it with `git log -1 --format=%H -- docs/operations/RESTART_HANDOFF_20260906.md`.
Last verified published and installed execution source:
`6b555075fcf553994ecac8e368f4676cbdffdc56`. Publication of this checkpoint must be
verified separately; a local commit is not evidence of a push.

## Actual state

Purchased Linux host bootstrapped with separate non-root driver, reviewer,
controller, worker and uncredentialed publisher roles. Root-owned immutable
release, synthetic-only controller/worker systemd timers, private outputs,
resource limits and firewall are configured. Working operator SSH preserved.
Node 22.23.2, Codex 0.153.4 and Claude 2.1.222 installed. No model sign-in done.
No new unattended model/research loop enabled; live 48/96 limiter remains inactive.

Read-only reconciliation is in HOSTED_SYNTHETIC_CHECKPOINT_20260906.json:
two Linux synthetic successes, one intentional failure, one blocked Colab job;
three outcomes and three pending-auth wakes. Successful payload SHA-256 is
`776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800`.
No scientific job is active. Server timers may safely continue without SSH;
oneshot services were inactive between ticks with Result=success. They cannot
consume pending model wakes without authentication and authorized bounded turns.
This is not proof of 24–48 hours laptop-disconnected operation, phone delivery,
remote Astra continuation, complete nightly review or provider backup recovery.

Runtime state: `/var/lib/research-system/research-controller`; private original
attempt consoles and outcomes: `/var/lib/research-system/outputs/<attempt-id>`.
Attempt IDs are preserved in the JSON receipt. Service journals:
`journalctl -u research-system-controller.service` and corresponding worker unit.
Private diagnostics: `/var/lib/research-system/runtime-diagnostic`.
Source: `/opt/research-system/current`, resolving to the immutable 6b555075 release.
No pending package installation is known; do not restart or resubmit any job on
that assumption. Reconcile actual processes, outcomes and state before retries.

## Work and verification

Implementation worker inventory completed its synthetic acceptance harness; its
work is committed. No implementation worker remains active. Local b670743 fixes
tracked .gitignore hydration and the installed CLI's `codex sandbox -- ...` syntax.
The exact .gitignore was hydrated remotely without changing source/job bindings;
this allowed already-submitted jobs to finish. Corrected sandbox verification is
NOT yet executed: the prior invocation incorrectly tried to execute `linux`.
The exact-binary AppArmor exception is installed; global userns restriction was
preserved. Do not overwrite the frozen release to apply the corrected test.

Prior release tests: 350 passed / 37 subtests. Latest targeted tests: 46 passed /
17 subtests. Review metadata in BOOTSTRAP_REVIEWS_20260906.json includes genuine
Claude approvals and earlier rejections. Latest author-operated Fable review of
b670743 APPROVE, with nonblocking findings: Git-version-dependent lazy-fetch
control, sparse repair lock race, distinction between downloaded Node checksum
and reviewed digest, expected versus measured CLI version, and login attestation
wording. Preserve these for follow-up; approval does not mean hosted checks passed.
No pending Claude review remains. These reviews do not replace independent merge
candidate review. Private originals and failed diagnostics must be retained.

## Exact next steps after return

1. Reconcile branch/local/remote refs and SSH agent availability, then inspect
   existing services, jobs and outcomes read-only. Preserve main, pilot, cfadeb1,
   551be01 and the frozen P001 checkout. No resets or duplicate dispatch.
2. Run the existing private collect helper for terminal synthetic jobs. It checks
   terminal status before restart/dedup/OS-boundary/backup sample verification.
   Its previous LINUX_NOT_COMPLETE failure preceded actual completion. It is not
   a new start command. Do not claim its acceptance checks already passed.
3. Apply only the reviewed corrected sandbox verification via a separately bound
   operations revision; preserve the installed scientific execution snapshot.
4. Migrate the three tasks below into the hosted queue and daily reports. Existing
   registrar supports two IDs; extending it must preserve prior source bindings.
   Current repository backlog is durable, but hosted registration is not proven.
5. Preserve primary evidence, publish permitted checkpoint through controlled
   publisher, verify remote pin/CI, and continue only then with grouped sign-ins.
6. Complete remote continuation, restart/dedup, backup restore, nightly review,
   phone response and protected permission acceptance before unattended research.

## Pending research tasks

Full definitions/dependencies: QUEUED_SCIENTIFIC_TASKS_20260906.json.
- Prediction charter: system-authored, linked pilot, admission-imaging goal,
  exploratory 99 / untouched 49, baseline plus two; Claude alignment review,
  applicable ratification, actual selected-charter pipeline use. Preserve old
  charters, scores and approvals. Missing original onboarding remains explicit.
- 047b: establish exact primary source/contract/original bundle/private evidence/
  successful console; avoid duplicate execution/import; validation, import,
  interpretation and opposing-family review only when existing gates permit.
  Historical Phase-B candidate is not proof of the operator's intended identity.
- Evidence propagation: inventory actual stage context; extend existing index,
  librarian and campaign builder using tags/source dependencies. Propagate actual
  permitted findings, limitations, negative results and predecessor Next-decision
  with dispositions. Pending 047 evidence stays pending; receipts are insufficient.
  Preserve blinding/scoring/approvals; relevance review, no automatic amendments.
  Demonstrate the actual path and obtain Claude review.

## Human dependencies and boundaries

Remote existing-subscription Codex device sign-in first, Claude sign-in second,
then concrete writer/reset/notification permission decisions; no new authority
implied. SSH key may require re-unlock after its agent lifetime expires. Private
connection details and exact sign-in commands stay in private deployment evidence.
Local sandbox approval prompts can suspend this session; the project inbox cannot
answer them. No guarantee this laptop session can run unattended under current
settings. Hibernation is safe for this checkpoint; it suspends local work, not the
already-running deterministic server timers.

Patient transfer/P001 launch, reserved cohort, 047 landing/cleanup/protection,
main merges, live limiter activation and new spending/credentials remain reserved.
Archive preservation receipt remains historical evidence, not a new live check.
Do not resume Colab, mount Drive, or launch P001 to demonstrate readiness.
