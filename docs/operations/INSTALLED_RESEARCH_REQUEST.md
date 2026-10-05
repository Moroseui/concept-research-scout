# Submit one installed research request

Humans and agents can queue the same prepared research task through
`Runtime.submit_research()` or the installed controller CLI's `submit-research`
operation. Submission records saved work; it calls no model, admits no turn,
starts no timer and creates no synthetic execution job. The existing controller
later runs its ordinary admission, campaign author/reviewer and disposition path.

A root-owned controller configuration may contain one `research_request`, mutually
exclusive with the legacy `campaign_preparation` completion-triggered request:

```json
{
  "task": {
    "mode": "discuss",
    "request": "Assess the supplied comparison evidence and next eligible action.",
    "task_id": "external-comparison-20260910"
  },
  "evidence_file": "/etc/research-system/live-research/research-evidence.json",
  "evidence_sha256": "REPLACE_WITH_EXACT_FILE_SHA256",
  "day": "2026-09-10",
  "initiator": {
    "kind": "agent",
    "family": "codex",
    "model": "gpt-6-astra",
    "session_id": "ACTUAL_PROPOSER_SESSION"
  }
}
```

Only the existing P001 `discuss` and `readiness` modes are supported. This is a
configured task, not a command or general experiment launcher. The initiator is
the attributed proposer of that prepared request, using the existing recorded
change actor schema; it is not an operator signature. Submission also records the
actual controller UID. Root administrative transport alone does not identify who
made a scientific judgment. Scientific stage attribution still binds the actual
Astra event and original opposing-model receipts.

The evidence file contains the prepared `reviewer_evidence` JSON object. It must
be root-owned, readable by the trusted configured controller GID, with no group
write or world access; use mode 0640 in a root-owned 0750 directory of that GID.
The reader rejects symlinks, changed hashes, wrong permissions, oversized files
and unsafe remaining transport content. Original bytes remain private. The full
request, source and input hash bind the saved task and both model contexts; inputs
are rechecked before execution and recovery.

For a separate installed controller, use its exact source and configuration:

```sh
python -m orchestrator.handover_runtime \
  --config /etc/research-system/live-research/controller.json \
  --human submit-research
```

Authenticated root callers use the same fixed `runuser` transport to the
`research-controller` identity. A controller-identity caller reaches the same
operation directly. The convenience `research-system-control` wrapper also accepts
`submit-research` for its installed default configuration; check that configuration
before using it with a separate controller. The existing source, peer, broker and
activation requirements still apply. This document does not install or activate it.

An identical submission returns the original task, including after a restart,
completion or later report-context changes. The task ID permanently binds its
first source/configuration/input identity. A changed request with that same task
ID fails with `RESEARCH_REQUEST_IDENTITY_CONFLICT`; inspect the original and prepare
a distinct reviewed request rather than editing or deleting saved records. SQLite
keeps submission and queue insertion atomic. Incomplete stage evidence still uses
the existing original-receipt recovery; submission never retries a model.

Use the same controller's `status`, `pause` and `resume` operations to inspect or
steer it. A paused task may be queued and inspected but cannot obtain new admission.
Resume neither resets the limiter nor enables a timer. Scientific human stops in
the existing campaign route remain enforced. Status reports the actual server
report directory and saved task identity.

Configured research reports, scientific artifacts, reviews and dispositions stay
private even when ordinary daily reporting has a configured publisher. This route
does not export a scientific result. Ordinary public reporting and its existing
publication-before-review gate are unchanged. Any later release of private science
requires its applicable publication authority and checks.

The hosted route preserves either opposing-review outcome after its one bounded
author/reviewer round. `APPROVE` records `REVIEWED_PROPOSAL_NOT_ADOPTED` and
`APPROVED_PROPOSAL_ONLY`. `REVISE` or `REQUEST_CHANGES` records `REVISION_REQUIRED`
and `NOT_ACCEPTED`, preserving the exact verdict and criticism. Astra receives
that original review for a disposition; a completed three-stage coordinator task
does not mean that the scientific proposal was accepted. A negative review cannot
be loaded by the approved-proposal adoption reader. The ordinary local pipeline
retains its existing repair rounds and revision-limit refusal.

Inspect `tasks/<task>/scientific-disposition.json` and `scientific-disposition.md`
under the configured state directory. They identify the original scientific
artifacts, exact opposing verdict, model sessions, disposition and authority
limits. The proposal and review stay in the recorded campaign output directory,
with protected broker replies as their independent source. These are scientific
task records. The generated operational report remains queued for its own review;
the system does not label scientific Claude output as a review of a report Claude
never received. Configured research delivery remains private.

Recovery reads original broker replies through `stage_status`; it does not make
a new model call or a fresh review. Missing derived files may be reconstructed in
a separate recovery directory while original files and failed-pipeline markers
remain intact. Exact review/status/acceptance bindings, artifact hashes and broker
reply comparisons must pass before disposition. Changing local artifact hashes
or coordinator receipts cannot replace the original criticism. A saved disposition
does not implement a repair or schedule another experiment: use the existing
recorded change/task route and applicable review for any subsequent work.


Retained catalog history has no lifetime ceiling of 32 entries. Each immutable task
remains available by its exact ID; that lookup checks the protected directory and
selected file without enumerating or reading unrelated entries. The same source,
evidence, eligibility, linked-change and saved-packet validation still applies.
`research-list` returns the retained history in task-ID order and identifies the
separate bound of 32 IDs in an explicit scheduling selection. Listing or retaining more
entries grants no admission, additional models, or scientific authority. No old
entry or result is removed to make room for a successor.
