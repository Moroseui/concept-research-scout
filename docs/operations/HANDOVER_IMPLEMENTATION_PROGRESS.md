# First handover implementation — current work record

Base: `7bba218e37b76a180d8ac35c34f2d30afe165143`, branch
`astra/infrastructure-milestone-record`. Prior hosted review and amendment remain
preserved; the readiness proposal is reviewed, not missing a review. No previously
successful run was repeated. SSH initially had no loaded identity; the operator
reloaded it and read-only access succeeded. Original five synthetic attempts and
five outcomes remained unchanged.

Current draft changes (not installed or approved for activation):

- Shared Actions/server admission uses the existing CAS ledger, separate server
  identities, common thresholds, duplicate binding and persistent midnight halt.
- Coordinator uses Store/SQLite and immutable stage receipts; a completed review
  survives disposition/bookkeeping failure. Missing receipts remain uncertain and
  cannot trigger blind retry. Independent eligible tasks progress past dependencies.
- Revision-bound pause/resume, read-only status and nightly identity dedup are
  implemented in the coordinator; production CLI/service wiring remains unfinished.
- Protected broker draft checks OS peer identity, exact destinations, approved source
  pins, operator-only reset with expected sequence/policy, and delegates to the
  existing publication and ledger primitives. Live grant remains inactive.
- Writer App credential adapter requests only the selected repository and explicit
  permissions, verifies returned scope, and removes temporary credentials from the
  environment on every exit. No App or credential was created or used.

Relevant synthetic tests currently pass. These are local implementation results,
not deployed acceptance. Remaining work includes the installed service/client
adapter, Actions provenance collection, persistent report/model handling and final
bookkeeping recovery, complete permission/ownership checks, hosted synthetic
verification and fresh Claude review. No permission packet is presented yet.

GitHub token-scoping implementation reference:
[GitHub App installation token API](https://docs.github.com/en/rest/apps/apps#create-an-installation-access-token-for-an-app).
The API supports explicit repository and permission restriction; a token or branch
name alone does not enforce our publication branch boundary.

Recovery wiring follow-up: a read-only broker status route verifies the original
console, prompt, answer and context hashes before returning a completed stage.
Absent evidence remains uncertain. Coordinator recovery records those originals
without invoking a model. Socket client disconnection no longer kills successful
bookkeeping. Report task identity excludes mutable review-queue status. Runtime
and broker integration remain drafts; no live activation is claimed.

The local Unix-socket regression needed sandbox permission for socketpair traffic
(`Operation not permitted`); it passed when run with that permission. SSH access
was restored by operator authentication. No model sign-in is currently requested.

Fresh source review at `306504d2664a848860f1aa45f2819ee29224236c` returned
REQUEST_CHANGES (actual reviewer `claude-fable-5`; author-operated, not merge desk).
The original findings and execution bindings are recorded in
`HANDOVER_RECOVERY_REVIEW_20260906.json`. Corrections enforce canonical role order,
isolate/cap final bookkeeping, distinguish pre-launch refusal from uncertainty,
and preserve control-write failures while processing subsequent valid requests.
A follow-up review is required; these corrections are not self-approved.

The selected 48/96 semantics passed a private synthetic ledger test: 48 warns,
96 admits and latches halt, 97 refuses, duplicate 96 does not recharge, and midnight
does not clear halt. No live ledger was initialized. Draft systemd units passed
`systemd-analyze verify` without installation or service activation.
The Actions artifact identity verifier is implemented and locally tested against
synthetic API metadata; actual protected API collection and workflow integration
remain unfinished. Socket unit contents now pass the same pre-publication text
scanner as other service units; forbidden case strings remain rejected.

Follow-up review at `6442ad8eae58577d8c2ec9cfb00998e9c851ef97` approved the
source fixes, with explicit next-phase gaps and no deployed-acceptance claim.
`HANDOVER_RECOVERY_FOLLOWUP_20260906.json` preserves the actual result.

A new isolated hosted component fixture at
`f1afc7bcb807057370efd549bb2b5c9eda4802ea` passed as UID 997, with zero model calls
and zero patient files. It recovered a saved fixture outcome, preserved the
completed predecessor, and rejected duplicate dispatch. Original five worker
attempts/outcomes and existing services remained unchanged.
`HANDOVER_HOSTED_COMPONENT_20260906.json` records the limits: operator controls
were library fixtures, and after-exit transient-unit properties did not establish
resource settings. Persistent broker/model/report service acceptance remains open.

Setup failures were retained privately: script compilation, unavailable promised
Git objects when locally packing the partial clone, missing prerequisite ref,
thin-pack delta bases, and incomplete checkout. No fixture job started on those
failures. A standard sparse clone prepared locally, with all 65 included blob
objects inspected as component code/bootstrap metadata, resolved source staging.
The partial snapshots and private command/console evidence remain preserved; none
was substituted for the original installed execution snapshot.

## Active goal batch — 7 September UTC

The CLI restart was reconciled at e478ad0 without replay. Scoped commits preserve
all prior edits: 35d48fb (service harness/context), a3d047a (source packaging,
fixture installer, numeric notification ordering), and 6863968 (review fixes and
actual socket evidence). These commits are local; the remote milestone still
needs controlled publication after review. No main or results ref was changed.

The source-only service review at 35d48fb requested changes. Its original receipt
is HANDOVER_SERVICE_REVIEW_R1_20260907.json. TasksMax=32 and checked predecessor
receipt reads are now explicit; the unneeded non-systemd socket fallback was
removed. The socket unit is included in reviewer evidence. Traversal is rejected
by the existing shared event validator, now regression-tested. An actual non-root
hosted Unix-socket fixture connected under ProtectSystem=strict and PrivateNetwork
without any new writable-path exception. A first fixture failed because umask made
its test directory non-traversable; original remote evidence is preserved.

A follow-up source review at 6863968 is pending. No model-capable fixture service
has been installed or started. Its prepared snapshot has 77 inspected code/context
blobs and no patient payloads. The installer refuses existing state, installs no
writer key, starts no service and enables no timer. The bounded acceptance harness
will run one three-call cycle and recover a deliberately withheld disposition
using original evidence without new model calls. It is not live authority.

Verification: 38 broader tests passed in the sandbox; the one Unix-socket regression
blocked by sandbox permissions passed separately outside it. Six archive-safety
checks and 23 focused follow-up tests passed. These results do not establish
installed service acceptance. The actual hosted transport fixture is separately
recorded in HANDOVER_SOCKET_SANDBOX_20260907.json.

Next: finish the pending review, address concrete findings, install/verify the
bounded fixture and perform its supervised first/recovery phases. Then complete
the protected publication import and Actions admission integration, final human
controls/report delivery, deployed review and concrete permission packet. Preserve
existing completed jobs; reconcile any new partial setup before retries. Live
writer/reset grants, limiter/unattended activation and scientific launches remain
reserved. The wider research tasks remain queued and are not handover prerequisites.

Service update at 03:36 UTC: R2 Claude source review APPROVED 6863968 (receipt
HANDOVER_SERVICE_REVIEW_R2_20260907.json). The fixture is installed, with no timer
or writer credential. First launch failed at systemd CHDIR (200) before Python:
archive directory modes inherited a private umask. The exact source tree was made
readable/traversable without changing bytes or tracked executable bits; non-root
checked_source passed. Private configuration/state/evidence modes were untouched.
The failed unit and original diagnostics remain preserved. The installer now has
an explicit tested source-mode normalization for future setup.

A fresh bounded first phase is RUNNING under unit
`research-system-handover-acceptance-first-6863968-r2`, source
`6863968863ddfb1d82b25c7b358857e666c950a5`. Protected turn identity:
`46f92feebb9d8475b2f979aa0d6225deaf1226b76fc71917858d64554920bafa-1`.
At last inspection continuation.started.json existed, no stage receipt/ended file
was present, and an actual non-root Codex process was running. Do not resubmit.
Read the fixed service status/receipt route before further action. Original
`research-system-handover` broker/socket now run for this supervised fixture;
its one-turn ceiling is fixture-only and no recurring timer is enabled. Once first
phase finishes, reconcile all three originals, then restart only the idle synthetic
broker and run the separately named recover phase in the same UTC day. Recovery
must make zero new model calls and leave the admission count unchanged.

Supervised service acceptance completed: actual Astra → Claude → Astra calls took
78.44 seconds total. The intentionally withheld disposition left the coordinator
BLOCKED while all three original model receipts existed. After an idle broker
restart (PID changed), the recover phase completed in 0.10 seconds with zero model
calls; admission count stayed 1 and duplicate polling/bookkeeping passed. Original
private console, protocol, state and failure evidence was copied to the private
evidence area. Checked artifacts are in hosted-service-acceptance-20260907/.
This proves the bounded installed service recovery path, not live activation.

The hosted reviewer accurately found that the empty fixture report omitted its
bound pending tasks and lacked post-recovery evidence (which did not yet exist).
Astra's original disposition accepted the readability fixes and qualified absence
of supplied science as absence of evidence, not proof of no progress. The report
renderer now preserves pending task context with its own hash and handles empty
execution periods plainly; 21 report/runtime tests passed. Earlier report bytes
remain unchanged. Recovery acceptance is now backed by the subsequent actual
receipt. A final fresh deployed-evidence review remains required.

An independent draft Actions transport now retrieves an exact run attempt, pinned
workflow bytes and one bounded artifact through the GitHub API. Token-free signed
storage retrieval is tested. It is not yet wired to polling/workflow admission or
activated. Official API references: GitHub REST Actions artifact download and
workflow-run-attempt endpoints. No writer credential or new API grant was used.
