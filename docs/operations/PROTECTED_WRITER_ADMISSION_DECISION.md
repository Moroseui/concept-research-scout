# Protected writer/admission/reset — proposed decision, inactive

The operator selected 48/96 but has not granted this design or live activation.
The notification App (4853010, installation 159584002) remains Issues write and
Metadata read only. Do not add Contents or Actions authority to that App.

## Proposed authority and ownership

Use the existing Git CAS admission ledger at one metadata-only ref,
`automation/dispatch-state`, for both Actions and server turns. Keep the existing
controller, queue and validators; do not add a second database or independent
server allowance. The ref is not initialized yet. Its schema must be extended
and reviewed to distinguish Actions run/attempt identities from server turn
identities before use; the current implementation accepts only Actions IDs and
two branches and is not yet a server admission adapter.

Propose a separate repository-selected GitHub App with Contents write, Actions read and Metadata
read on `Moroseui/concept-research-scout` only. No Administration, Actions write,
workflow-edit, pull-request-write or organization permissions. The exact App and
installation IDs would be recorded after a separate operator creation step. Its
key would be held solely by a non-login protected publisher identity, with code,
policy and service units owned by root outside all model-writable paths. Models,
scientific workers and ordinary Actions jobs must never receive that key or its
installation token. No such credential is authorized or installed by this packet.

Allowed destinations are exactly `astra/infrastructure-milestone-record` and
`automation/dispatch-state`. Main, pilot, results and all other refs refuse. The
state route accepts only schema-valid ledger transitions, not arbitrary Git trees.
The code route requires exact repository/source/baseline/destination bindings and
checks every outgoing object/version before transfer. Artifact, report and
notification content uses the same fail-closed export boundary before upload.
Missing destination creation uses the existing absent-ref atomic publisher.

**Actual limitation:** Contents write is repository-wide; the App credential alone
cannot restrict writes to these two refs. A compromise of the protected broker or
operator-held key can bypass application checks. Existing owner credentials and
GitHub administration can also push directly. Preserve main/results protections;
review installed rulesets and available plan capabilities before granting a bypass
exception. Do not claim universal prevention from CI, hooks or branch naming.

## One narrow request interface, no model-held writer token

Server requesters use a Unix socket authenticated by OS peer UID. The broker accepts
only fixed admission, status and checked-publication schemas; no shell command,
path traversal, arbitrary environment or reset verb is accepted from the driver.
Use one protected branch lease and durable turn identity before invoking a model.
The broker, not the driver, mints and uses the short-lived GitHub token.

Actions use an admission-request artifact from a separate, credential-free admission
job in a pinned reusable workflow. The artifact has a fixed schema and passes the
existing export check before upload. The protected broker polls GitHub's Actions
API for known outstanding requests, verifies repository ID, run ID, attempt,
workflow path and reviewed workflow/source identity, and retrieves the immutable
artifact using its Actions-read permission. No credential or OIDC bearer is placed
in the artifact. Request text never selects arbitrary commands or reset operations.

The broker writes admission to the one Git CAS ledger. The waiting Actions job
reads that public metadata-only ledger and proceeds only on an exact matching
run/attempt/source admission. Timeout produces a visible block, not permission to
run. Proposed broker poll interval is 30 seconds while requests are outstanding;
maximum admission-job wait is 10 minutes. This consumes ordinary Actions runner
minutes and API requests; it is not a financial cap. Server turns enter the same
broker through the UID-authenticated socket. Notifications use the separate
notification-only App after content checks.

This reuses GitHub artifacts, the existing ledger and the purchased host. No public
server endpoint, new inbound firewall rule, TLS/domain purchase or managed queue
is needed. No additional GitHub writer token is distributed to Actions. Exact
reusable-workflow source allowlists, artifact/run replay tests and broker polling
are implementation/verification prerequisites, not deployed claims. Existing
workflow model secrets can still be used by another permitted workflow that skips
this route; their restriction/removal must be explicitly reviewed before claiming
global enforcement. Do not silently broaden or repurpose them.

## Reset and counting

Reset is a separate local fixed-command interface restricted to the operator's
SSH-authenticated administrative account. It requires the exact expected state
sequence, policy hash, decision reference and authenticated operator identity;
records a durable audit event and refuses stale/replayed requests. The driver,
notification App, Actions artifact admission route and scientific worker cannot invoke it.
Phone ACKs never reset the ledger. A narrow operator-only sudo rule for this exact
installed reset command would require approval; do not give the driver sudo.

One admitted top-level server Astra turn includes at most three synchronous model
calls with individual time/usage receipts. A fresh asynchronous resumption or
nightly Claude review is a new admission. A retry after a terminal model failure
is a distinct attempt; recovery of the same admission alone does not charge again
or authorize duplicate model execution. Larger stage budgets need explicit review,
not a hidden unlimited child-call envelope. Deterministic polling and report
bookkeeping consume no admissions. Existing Actions control run/attempt counting
is preserved. These are proposed server semantics, not newly ratified policy.

At admission 48 persist a warning and continue. Admit 96, persist the hard notice
and latch a halt for subsequent admissions. Do not kill admitted work. UTC-day
rollover clears ordinary daily counts but never the halt. Failures receive no
refund. The same shared policy applies across branches and backends. Limits are
job/turn counts, not dollars; existing Codex API and Claude subscription billing
arrangements remain unchanged. No automatic paid fallback.

## Activation sequence and decision scope

1. Independently review the installed broker, exact workflow and artifact identities,
   ownership, credential/ruleset limitations and operator-only reset interface.
2. Operator approves this completed permission design and exact credential grant.
3. Initialize shared state once through the protected route, preserving its pin.
4. Use synthetic policy/state to verify concurrency, restart, duplicates, 48/96,
   midnight halt persistence, warning delivery, wrong-UID/artifact-source/reset rejection,
   forbidden publication and failure-without-refund. Then verify live policy
   configuration without exhausting the live allowance merely to test a limit.
5. Seek the separate live unattended activation decision and 24–48 hour observation.

No approval is requested for an incomplete broker/workflow implementation. Until these
steps pass, supervised synthetic setup can continue under its bounded authority;
standing dispatch, writer installation and limiter activation remain blocked.
