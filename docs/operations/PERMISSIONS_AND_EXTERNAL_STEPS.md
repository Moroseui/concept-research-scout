# Remote operating permissions and external steps

**Proposal and dependency packet. No permission or activation is granted by this
document.** The purchased Linux host is the deployment target. No patient launch,
new paid product, main merge or 047 operation follows from bootstrap acceptance.
Connection details remain in private deployment configuration.

## Current verification update

Both server model accounts have authenticated and completed real bounded calls; see
HOSTED_CYCLE_RESULT_20260906.md. Notification-only App installation, actual device
delivery and authenticated synthetic acknowledgment are now verified in
NOTIFICATION_APP_IDENTITY_20260906.json. Do not repeat sign-in or App setup absent
a new failure. Operational phone replies remain disabled. The older preparation
steps below are retained as setup context, not a statement that authentication is
still missing. DEPLOYMENT_CLOSEOUT_CHECKLIST.md tracks current remaining evidence;
PROTECTED_WRITER_ADMISSION_DECISION.md specifies the proposed protected boundary.

## Protected writer, admission and reset design

Proposed ownership separates the non-root Astra development identity, scientific
worker, and protected controller/publisher. Root owns installed publisher code,
destination policy, service definitions and admission/reset interfaces outside
agent-editable checkouts. A dedicated controller identity owns private application
state; developer and scientific-worker identities cannot modify protected admission
state or invoke reset. Scientific attempts receive pinned code, bounded inputs and
private output access, without GitHub administration or model credentials. The
driver receives no unrestricted sudo. Administrative setup is not standing agent
authority.

All publication must pass the protected publisher's outgoing-history and content
checks with exact repository, source, baseline and destination bindings. Its policy
permits only the explicitly authorized development branch; main and results refs
are denied. An agent-editable Git branch or a repository token alone cannot enforce
this boundary. Do not install unrestricted GitHub write credentials in the driver
or worker. The concrete credential scopes, protected installation and authenticated
request interface still require operator approval and adversarial verification.

N=48 and hard threshold 96 are selected; live activation remains conditional.
Proposed server accounting charges one top-level admitted Astra turn, including
its synchronous bounded child stages. Each child retains model/usage receipts and
explicit count, timeout and resource limits; it is not an unlimited quota escape.
An asynchronous completion that starts a new driver turn is a new admission.
Recovery of the same durable admission identity is idempotent and is not charged
again. Deterministic polling, reconciliation and report bookkeeping are not model
admissions. A fresh nightly Claude review needs its own explicit governed request;
publishing its output or Astra's disposition must not recursively trigger reviews.

Admission 48 persists notification and continues. Admission 96 is permitted,
persists the hard notification and latches a halt for subsequent admissions.
Ordinary UTC-day counts roll over; the hard halt survives midnight until the
authenticated operator resets it. Already admitted jobs are not killed, failures
are not refunded, and the agent cannot raise thresholds or reset itself. Reset
requests must bind operator identity, exact policy/state version and explicit
action; stale or replayed requests refuse.

Actions and server requests must use one protected admission authority across
branches. Routing Actions into that same broker, writer permissions and operator
reset authentication are **not yet authorized or deployed**. Preserve the existing
Actions counting semantics while reviewing the migration; do not run two independent
48/96 ledgers and call them a shared cap. A job-count ceiling is not a dollar cap.
Activation requires approved permission design, initialized shared state and hosted
warning/halt/restart/duplicate/reset tests before unattended overnight authority.

## Grouped operator steps and dependencies

1. **Existing model sign-ins, after compatible clients are installed.** The remote
   driver must select exactly `gpt-6-astra`; unavailable model, quota or authentication
   is a recorded block, never permission for substitution or paid fallback. Supply
   the exact installed-client sign-in commands in the deployment checkpoint and
   complete each browser/device interaction privately. Preserve other agents' roles
   and the existing Codex API / Claude subscription arrangements. No model or GitHub
   credentials are established on the server by this packet; actual authentication
   requires a separate receipt. Missing model authentication blocks its affected
   review/driver stage while deterministic supervised synthetic work continues.

2. **Approve one concrete protected writer/reset and notification configuration.**
   Review OS ownership, permitted branch, GitHub permissions and authenticated
   broker/reset endpoints together before credentials are installed. The proposed
   phone route uses a dedicated service identity posting checked GitHub decision
   notifications. A device test must demonstrate actual GitHub Mobile delivery and
   an authenticated operator response bound to the exact decision/source version.
   Responses select validated enum actions; comments are never shell commands.
   Notification identities deduplicate delivery, routine questions form a digest,
   and only timely exceptions interrupt immediately. A commit or self-mention does
   not establish phone delivery.

3. **Optional Spaces setup, still a separate purchase.** The planned Standard
   service is quoted at $5/month and has not been created. If approved, the operator
   creates one private bucket (proposed name `research-system-private`; availability
   unverified) in a selected supported region, keeps file listing and object access
   private, and creates only the required bucket-scoped access. Do not enable public
   CDN/object ACLs or give scientific workers account-wide keys. Keep write authority
   separate from read-only recovery tests. Record the actual endpoint, scopes and
   credential placement privately; initially test only a synthetic state/output
   sample. Patient archive transfer remains separately gated. If suitable scoped
   access cannot be expressed by the provider, stop for that exact permission
   decision rather than substituting broad access. Existing host plus quoted backups
   totals $115.20/month before taxes/overages; this planned service would make $120.20.

4. **Account and recovery evidence.** DigitalOcean account two-factor authentication,
   actual backup enablement/first backup and a provider restore are not verified by
   this packet. Operator inspection should confirm them without sharing recovery
   codes. Restore a consistent private synthetic application-state/output sample and
   verify its identities; a selected backup checkbox is not recovery proof. Preserve
   working administrative access while reviewing firewall and replacement access.

5. **Reporting schedule.** Proposed daily time is 21:00 America/New_York, not yet
   selected. Reports and fresh Claude reviews require independently recorded hosted
   acceptance. This schedule does not change the admission ledger's UTC boundary.

## Permission prompts and reusable setup boundaries

Distinguish local execution-sandbox approvals, SSH/OS access, client tool approvals,
model sign-in/quota failures and reserved operator decisions. An accepted shell
command does not authenticate a model or ratify a scientific launch. Record the
actual refusing component and its stated reason once in the inbox; do not infer
that every prompt needs broader server permissions.

Reusable local approvals should cover fixed read-only status commands or versioned,
exact bounded bootstrap operations with explicit arguments and reviewed payloads.
Do not approve arbitrary root SSH, arbitrary script execution, unrestricted sudo
or broad permission disabling as a convenience. Preserve original evidence and
continue independent authorized work while an external dependency remains blocked.

## Current-session unattended limits

The local Codex session still uses the managed workspace-write sandbox. Writes to
Git metadata or private evidence locations and network/SSH setup can require the
CLI approval gate. A pending approval suspends that tool call; the project inbox
cannot answer it. The SSH agent also has a finite identity lifetime. Existing
exact-command approvals are reusable for matching operations, not blanket setup
permission. No uninterrupted local-session guarantee is made.

Consolidate deployment into the reviewed installer at an exact published pin and
a fixed synthetic acceptance command; preserve raw setup logs privately. Read-only
status collection can reuse exact approved commands. Do not propose reusable
arbitrary root SSH or Python prefixes: they would permit unrelated administration.
A genuinely narrow future reusable interface should be a protected, fixed-action
status/setup broker with validated arguments. Its OS boundary and any credential
change belong in the permission packet, not an agent-editable shortcut.

The installed synthetic timers use no model and need no interactive command
approval. Once their hosted verification passes, they can continue after SSH
closes. That does not enable an unattended Astra driver: model authentication,
bounded-turn integration, shared admission permission and hosted activation still
have separate dependencies. No broad permission disabling is used to bridge them.
