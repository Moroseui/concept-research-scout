# Proposed dispatch admission — inactive pending operator choices

Measured record: [48 workflow_dispatch runs](DISPATCH_ACTIVITY_20260906.json)
over 28 UTC calendar dates (last date partial), daily peak 12, no recorded rerun
attempts. Proposed N=48 (4× peak), hard ceiling 96. Deleted/unavailable history is
not measurable. Job counts are not model-call or dollar caps. Authentication is
the existing Codex API key and Claude subscription OAuth, not two subscriptions.

`configs/pilot/dispatch-limiter.json` has status PROPOSED, n=null, no operator
approval, no reset operators and no writer permission. The workflow's preparatory
step reports PROPOSED_NOT_ACTIVE and grants nothing. Existing bounded dispatch
authorizations are separate; no standing at-will authorization is inferred.

The core `admit` operation is shared by all controls/branches through one
metadata-only Git ref (`automation/dispatch-state`). It reads a committed state,
computes admission, validates its complete schema, and atomically appends using
a before-pin lease. A concurrent loser reloads, at most 12 tries, then refuses.
Missing state, failed authentication/write permission, corruption and clock
rollback fail closed. Policy bytes bind the ledger so a different branch cannot
choose a new N without an explicit reset. State is capacity-bounded (10,000 event
records / 1.4 MB); exhaustion requires deliberate maintenance, never silent pruning.

The complete semantics, including UTC midnight, job attempts/replays, no refunds,
latched hard halt, operator reset and notification channel, are in proposed R3.
Notifications persist in the state before admission returns; a crash after the
commit cannot erase the charge or warning. Recovery of the same run/attempt does
not charge again and re-exposes pending notices. This is admission idempotency,
not a guarantee that a downstream experiment executes exactly once.

## Verification

Tests exercise 24 concurrent requests against one real Git ledger with N=4:
exactly eight admissions, the rest halted; main and pilot share the ceiling.
Tests cover N notification without halt, 2N latch across midnight, UTC rollover
below the cap, rerun attempts, duplicate identities, crash after CAS before
acknowledgement, durable warning recovery, explicit reset/stale reset refusal,
policy drift, malformed data and capped CAS failure. Two independent disposable
repositories also use the actual remote Git fetch/leased-push transport against
a disposable bare repository and detect a stale writer. No public state ref is
created and no model/patient job is run by these tests.

## Activation and reset preparation

After the operator ratifies a selected N and an exact permission design, initialize
an orphan metadata-only state ref with `initial()` through the reviewed `GitLedger`
implementation, bind the ratified config, and verify the hosted writer can update
only that state. An operator reset calls `reset()` with an authorized operator,
decision reference and exact expected sequence; keep the original approval record
privately/versioned as appropriate, while the public ledger stores its SHA256.
The function does not authenticate a human from a JSON role string: its caller
must establish operator authorization outside the agent's model process.

The current read-only Actions token cannot initialize or update this ref. Merely
changing status to RATIFIED is not activation: operator_approval, a chosen N,
state_write_permission, initialized state and a reviewed isolated writer route
must all be supplied. No new credential, Actions permission or state ref is
provisioned during this closeout. Hosted N/2N notification delivery and production
shared-state persistence remain unproven until that permission decision and a
bounded acceptance run. The local/remote-fixture tests establish implementation
behavior, not deployed enforcement.
