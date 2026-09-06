# Post-merge governance ratification — 2026-09-06

Recorded by Astra from the operator's explicit post-merge message. This records
human ratification, not agent approval on the operator's behalf. The source is
CLOSEOUT_RULINGS_PROPOSED.md at merged main d24ffb9003a2291f359afe3acf4bf491f2d7fd9f.
That historical proposal and prior approvals remain unchanged. R1, R2 and R4 are
ratified; R3 is ratified with the activation condition below. No new main merge
is authorized. Preserve cfadeb1b3ef250e981c596b4d36a75fff7e11b3d and include this
record in the next appropriate milestone PR.

## R1 — ratified

Side branches are agent workspaces. During development, the author chooses when
to invoke internal model review. Each merge into main requires independent desk
review of the actual candidate and an operator signature; depth follows the diff,
with particular care for orchestration, workflows, scientific execution and
governance. Keep branches milestone-sized. Existing scientific contract and
opposing-family experiment gates remain in force.

Every authorized automation route must validate outgoing content **before** Git
publication, Actions artifact upload or Summary release, on every destination it
supports. All automation must use the controlled publisher, including checkpoint
pushes. A request inventory is not a privacy review or human signature. Post-push
CI is additional detection and cannot undo exposure. The present local admin
credential can bypass these scripts using Git or GitHub APIs, and main has no
server protection. Therefore universal pre-publication enforcement is **not yet
established**. Before claiming it, the operator must approve an exclusive,
restricted writer design and removal of direct credential bypass; no credential
scope or repository permissions change under this proposal.


## R2 — ratified

The 78 bootstrap pilot commits through `1ecc3f9` used the operator's Git identity
for agent work. That metadata is preserved; the task record identifies the Codex
implementation lead and separately attributed Claude workers/reviewers. It is not
proof that the operator authored or signed off on each change. Going forward,
Astra-authored commits identify `Astra (OpenAI agent)`; other agents identify their
own authorship. Operator review/sign-off is a separate recorded decision, never
inferred from committer email. No history rewrite.


## R3 — ratified conditionally; selected N=48, hard threshold 96; inactive

The operator selects N=48 and hard threshold 96. Corrected R3 is ratified with
this condition: standing dispatch authority takes effect only after the operator
approves the concrete writer/reset permission design, shared state is initialized,
and hosted activation verification passes. All three are required; none is inferred
from this record, tests or PR #2's merge. The limiter is not active.

Reset authority remains exclusively the operator's. Existing Codex API-key and
Claude subscription OAuth arrangements are unchanged. There is no additional
spending, credential or provisioning grant. A job-count cap is not a dollar cap.
Existing scientific, compute and reserved-decision gates remain mandatory.

One admitted control-run attempt counts across main/pilot and all seven controls,
identified by run ID plus attempt. Admission retries are idempotent; new rerun
attempts and artifact-replay dispatches count. Admission precedes model use and
input validation; admitted invalid, failed or cancelled attempts are not refunded.
Unadmitted runner work and unrelated/bypassing routes remain outside this count.

Admission 48 persists notification and continues. Admission 96 is allowed and
latches a halt for later admissions; already admitted work is not cancelled.
Ordinary counts roll at 00:00 UTC; the persistent hard halt survives midnight
until an explicit operator reset. Reset starts a new epoch, retains prior events
and notices, and requires the current sequence plus separately authorized operator
evidence. Policy changes require reset, so another branch cannot silently increase
N. Notifications use the durable outbox and validated Actions Summary/warning;
phone/email delivery is not guaranteed. Recovery can repeat notices. Admission
idempotency does not authorize restarting an ambiguous patient job.

The runtime configuration remains PROPOSED/n=null/NOT_GRANTED during this
record-only closeout. The selected 48/96 thresholds are binding governance inputs
for the future approved activation, not a claim that the current configuration
has been deployed. The three activation dependencies remain in the decision inbox.

## R4 — ratified

047 scientific acceptance/landing, public-results history cleanup and P001 launch
each require separate explicit operator approval. Merging infrastructure is none
of those approvals. The queued 047 registry is not scientific acceptance. Keep
original evidence, exclusion/disposition questions, missing-console gates and
validation/import/interpretation requirements intact. Do not begin the queued 047
landing merely because the infrastructure PR merged.

