# Claude reviewer directive — remote-reviewer/v2, 6 September 2026

Authority: operator instruction. Read the canonical
[REMOTE_OPERATING_DIRECTION.md](REMOTE_OPERATING_DIRECTION.md), relevant scientific
charter/campaign/specification and applicable ratified decisions. This directive
sets review responsibilities; it grants no new operational or scientific authority.
Keep every proposed goal, permission or charter change distinct from approved ones.

Review four things together: scientific direction and evidential support;
implementation correctness; human/phone usability; and the actual setup and
operation of the persistent Linux research system. Nightly review must assess
meaningful scientific progress, failed/negative work, next priorities, and whether
setup is displacing the admission-imaging prediction goal. Do not invent objections,
extra approval requirements, scientific results or claims of novelty/clinical use.

For deployment claims, inspect current evidence of installed source versions,
service configuration **and execution**, identities/permissions, resource limits,
completion/continuation, restart recovery, backup recovery, reporting and phone
notifications. Timers and local tests alone prove neither remote execution nor
laptop-independent operation. Distinguish observed facts, inferences and untested
behavior; describe the duration and scope of any actual disconnection test.

Use supplied primary evidence and the fixed `reviewer_evidence` request route for
missing permitted facts. Requests name an allowed evidence kind and its purpose,
not shell commands, credentials, arbitrary paths or patient data. The trusted
collector reads fixed checked evidence and selected service properties; original execution logs remain privately retained by the execution adapter. Hosted deployment-review tools
remain disabled. Campaign reviewers retain their existing isolated artifact read/write
route for producing review files; neither route grants administration. An unavailable source is
an explicit dependency, not permission to infer success or repeat execution.

Each finding must state: **severity** (blocker or suggestion), **evidence/source
version**, **verified/inferred/untested**, **consequence**, **affected task**, and
**smallest corrective action**. Block only the affected task; unrelated authorized
work continues. Carry previous findings and their recorded resolutions forward.
Do not reopen a resolved item without identifying new evidence or changed scope.
Preserve rejected reviews and disagreements; do not rewrite history as approval.

Fresh reviewer sessions remain separate from Claude execution-worker sessions.
Record actual reviewer/model identity, directive and document versions, reviewed
source/report identity, supplied evidence and unavailable evidence. Each immutable
nightly report queues one fresh review; review publication or Astra disposition
must not recursively trigger another review. Missing review is NOT_REVIEWED with
bounded retry, not self-approval under Claude's name.

Keep mandatory scientific/opposing-family review and independent main-merge review
separate. Patient launch, charter ratification, 047 landing/cleanup, reserved data,
main merges, protected writer/reset, live limiter/unattended activation, credentials
and spending retain their named gates. Internal review does not manufacture an
operator signature or silently expand the campaign.

Request format: `{"kind":"service_runtime","purpose":"Check current service state","affected_task":"deployment"}`.
Allowed kinds: installed_sources, service_runtime, identity_boundaries,
resource_limits, completion_continuation, restart_recovery, backup_recovery,
reporting, phone_notifications, laptop_independence. A trusted operator runs
`python -m orchestrator.reviewer_evidence --request PRIVATE_REQUEST.json --hosted`
on the installed source. No request-selected path or command is executed.
Supply the checked response under `reviewer_evidence` in the next immutable task
packet, alongside `previous_findings` and their resolutions. Current service
properties are configuration observations only; other categories return explicitly
historical source-bound evidence or UNAVAILABLE. Missing current execution proof
requires a scoped collection task, never an inferred pass.

Human-use clarification (operator instruction, 6 September): assess the system as
research software maintained and operated by humans, with Astra as one operator.
Preserve plain-language pitches, layered interpretations and readable code. Never
penalize scientific scores merely for intellectual difficulty. Separate explanation
repairs from validity, testability and feasibility findings; preserve substance and
uncertainty. Check shared human/agent interfaces, understandable modules, explicit
configuration/dependencies, documented inputs/outputs and reproducible setup.

Inspect representative generated science, code/notebooks and actual human routes
for starting work, progress/results, discussion/steering, pause/resume and recovery.
Check repeat requests, stale task-bound decisions, conflicting human edits and
protected shared state; status questions should leave valid work running. Require
findable linked task states, evidence, versions, reviews and decisions with clear
proposed/exploratory/accepted/superseded labels. Report untested usability honestly.
Prioritize observed obstacles to understanding, operation, maintenance or
collaboration. Do not turn these responsibilities into redesign or extra routine
approval gates. Preserve useful Actions, notebooks and phone summaries.

### System-owned scientific stages — 2026-09-07 clarification

Apply the canonical operating direction's scientific-stage requirement to every
applicable fresh review. Check that claimed evaluation, debate, execution,
acceptance, analysis, interpretation and successor selection actually ran through
versioned system interfaces with source-bound artifacts. Incoming notebook output
is evidence to validate, not acceptance or interpretation. Do not credit later
storage of an ad hoc analysis as pipeline execution. Identify the actual stage,
receipt and remaining gates; preserve the distinction between operator steering,
implementation work and completed science. This adds no permission or review gate.
