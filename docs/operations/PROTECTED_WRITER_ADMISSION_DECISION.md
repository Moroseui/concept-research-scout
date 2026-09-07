# Protected writer/admission/reset — proposed decision, inactive

The operator selected 48/96 but has not granted this design or live activation.
The notification App (4853010, installation 159584002) remains Issues write and
Metadata read only. Do not add Contents or Actions authority to that App.

## Proposed authority and ownership

Use the existing Git CAS admission ledger at one metadata-only ref,
`automation/dispatch-state`, for both Actions and server turns. Keep the existing
controller, queue and validators; do not add a second database or independent
server allowance. The ref is not initialized yet. The draft adapter now distinguishes Actions run/attempt identities from server
turn identities in the same CAS ledger. Synthetic shared-ceiling and concurrency
tests pass. This is neither hosted activation nor approval of the server admission
semantics. Trusted Actions collection is implemented and tested; live credentials and hosted activation remain open.

Propose a separate repository-selected GitHub App with Contents write, Actions read and Metadata
read on `Moroseui/concept-research-scout` only. No Administration, Actions write,
workflow-edit, pull-request-write or organization permissions. The exact App and
installation IDs would be recorded after a separate operator creation step. Its
key would be held solely by the protected broker identity described below, with code,
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
GitHub administration can also push directly. The current authenticated [boundary audit](GITHUB_BOUNDARY_AUDIT_20260907.json) found only results deletion/non-fast-forward protection, **no main branch protection**, and no environments. Preserve the results rules; main protection must be established under a separate approved setup step. Do not claim universal prevention from CI, hooks or branch naming.

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

## Implementation reconciliation (still a proposal)

The installed synthetic handover broker combines fixed role launching and the
protected request interface. This packet now explicitly proposes retaining that
combined boundary; it does not claim a separate non-login publisher exists. The
actual non-root service, recovery and human controls are evidenced in the dated
receipts. No live writer key, shared remote ledger, or unattended timer is installed.

The smallest proposed final boundary retains the root-owned fixed broker rather
than introducing another daemon: root is needed only for the existing fixed
runuser launches into research-driver and research-reviewer. The broker accepts no
caller-supplied command, user, executable path or environment. App credentials
exist only inside its serialized authentication context, which closes before a
model launch; model subprocesses use the existing empty-environment, separate-UID
launcher. Root configuration, installed code, publication cache, ledger and reset
request files are outside model/controller write access. This narrower combined
privilege design requires explicit review and operator approval before any key is
installed. It is not an assertion that a separate non-login publisher exists.
No standing root shell or sudo capability is proposed for Astra. Source upgrades
of the protected boundary remain administrative deployment operations, distinct
from ordinary branch development and permitted scientific jobs.

## Current implementation facts, 7 September

Candidate staging and outgoing-history checks passed a fresh hosted direct-broker
fixture at 386cde2, with no credentials, service change or Git publication. It is
not a new Unix-socket identity test. Actual earlier socket, non-root recovery and
human controls retain their separate evidence pins. Latest source suggestions
bound report task histories and isolate malformed archive failures; these fixes
need their final review/deployment evidence.

The generated reusable Actions workflow now has a prepared request/upload/wait
route. While policy is PROPOSED, existing authorized manual controls retain their
inactive-limiter behavior; this grants no standing dispatch. The activated route
requires a genuine updated human-controls review receipt, a protected reviewed
source/workflow allowlist and initialized shared policy. The collector discovers
only matching in-progress runs with uploaded request artifacts, then verifies the
exact attempt and bytes before CAS. Each invocation bounds inspection and requests;
failed reads have three durable attempts. The waiter times out after ten minutes
and never writes state. This workflow change still needs the separately approved
main integration before main's buttons use it.

GitHub's [reusable workflow reference](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
associates the github context with the caller. The request therefore binds the
caller path from GITHUB_WORKFLOW_REF and its bytes at GITHUB_SHA; the protected
allowlist must approve that caller and the same-commit reusable implementation.
The existing reviewed-source check supplies the complete code binding, rather
than treating a caller filename as scientific or permission authority.


A necessary separate GitHub permission decision remains: repository-level model
secrets let older or otherwise permitted workflows bypass shared admission. Before
claiming shared enforcement, propose moving the existing Codex API and Claude
subscription credentials into a dedicated environment restricted to reviewed main
workflows, updating those jobs to request that environment, verifying a bounded
canary, and only then removing the repository-level copies. Preserve the original
private credentials throughout; this is a scope restriction, not new API billing.
Legacy pilot workflows would then lack model credentials; their supported human
replacement is the reviewed main controls. No secret relocation, environment
creation, workflow dispatch or restriction change is executed by this proposal.
Exact current GitHub protection capabilities and administrator bypass remain part
of the final operator packet and hosted activation verification.

## Concrete grouped operator decision (not yet granted)

Approve or amend the following design as one permission packet, separately from
activation. The requested scope is preparation of the existing host's protected
writer and shared admission/reset route; it does not authorize science or main merges.

1. Create a **separate** repository-only writer App: Contents read/write, Actions
   read, Metadata read; no Workflows, Administration, Issues, or Actions write.
   Record its actual App/installation IDs before use. Keep its private key in a
   root-only file under `/etc/research-system`, inaccessible to model identities.
   The existing notification App remains unchanged. Without Workflows write,
   commits changing Actions workflow files are a deliberate publication exception,
   requiring a separately approved infrastructure publication route.
2. Authorize the root-owned fixed broker design above and its two explicit refs.
   Keep a separate protected Git cache and ledger; put the non-root report author
   checkout under `/var/lib/research-system/handover-controller/author`, already
   covered by the controller unit's state-path allowance. This is a checked
   application boundary, not a claim that a repository-wide key cannot bypass it.
3. Approve shared server admission semantics: one top-level turn contains at most
   continuation, fresh Claude review, and Astra disposition; distinct async wakes
   and nightly turns are new admissions. Duplicate recovery is not. Ratified
   48/96, persistent halt, UTC counting and failure/no-refund rules remain unchanged.
   An authenticated operator alone may use the fixed reset interface with expected
   state sequence, policy hash and decision reference. No phone reset or agent sudo.
4. Approve a separate GitHub restriction rollout: main requires a pull request and
   the existing `basic` check, rejects force pushes/deletion, and grants no writer
   App bypass. Independent desk review plus explicit operator merge approval remains
   required even if GitHub's required reviewer count is zero for a solo maintainer.
   Move existing model secrets into a dedicated environment restricted to reviewed
   main controls, run a bounded canary, then remove repository-level copies. Preserve
   originals privately throughout. No restriction or credential move has occurred.
5. Approve informational threshold/report/block notices using the existing App.
   Replies remain acknowledgment only. Select a nightly time; **21:00
   America/New_York is proposed**, distinct from UTC admission accounting.

After these decisions: one-time state initialization, deployed permission/identity
and notification checks, then a **separate** explicit unattended activation decision
before 24–48 hours of observation. Do not interpret design approval as activation.
Existing owner credentials and administrators remain bypass routes; do not claim
universal prevention. Current main workflows cannot consume the new admission route
until their separately reviewed merge. No new subscription, model credit, paid
service or broader scientific envelope is requested.

Notification limitation: delivery deduplicates each exact event and caps its retries
at three, but has no aggregate daily issue ceiling. The initial supervised fixture
keeps notifications disabled. The proposed live configuration sends only fixed
thresholds, checked reports and bounded task-block metadata; review the finite task
allowlist/cadence at activation. Do not infer a global notification or dollar cap.
Phone acknowledgments expire after 24 hours and never execute decisions.

If report preparation leaves an unpushed candidate, subsequent publication remains
queued behind that preserved candidate until exact remote/local reconciliation.
No automated reset, overwrite or discard is authorized to clear that condition.
