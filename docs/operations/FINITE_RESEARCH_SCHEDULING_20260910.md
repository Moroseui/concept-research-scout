# Finite catalog scheduling

An installed controller can optionally select a bounded backlog without a client
prequeuing every task. The configuration is disabled when `research_schedule` is
absent or null. Its only accepted enabled form is:

```json
{
  "research_schedule": {
    "task_ids": ["p001-readiness-after-linux-handoff-20260910-v1"]
  }
}
```

The list contains 1–32 distinct catalog IDs in priority order. This configuration
does not create entries or authorize science. Each named entry still needs its
installed immutable request, exact source/evidence, actual scientific eligibility,
applicable linked version review and current predecessor disposition. A missing
entry is pending. Negative or pending review never becomes approval. A source or
question revision needs its own reviewed entry and scientific decision.

Each normal Runtime tick handles control intake before catalog selection. Selection
holds the existing writer/admission locks, checks pause and failed control transport,
then uses `Runtime.submit_research(task_id, submitted_by=...)` for at most one new
submission. Existing saved submissions are retained after restart, including
completed or blocked results. A blocked first entry does not hide independent
eligible entries later in the list. Coordinator admission and each affected model
stage still check the original live gates; selecting a task grants no model call.

The saved submitter is `kind: service`, with the actual configured controller UID,
source and `finite_catalog_submission` operation. This identifies transport only;
it does not claim a particular human, model or provider session. It is accepted only
as the exact Runtime service submitter. Change-request proposer/authorization roles
remain human or agent. The entry's original proposer and actual scientific model
judgment/review remain separate and unchanged. Humans and agents still submit and
inspect through the same underlying Runtime operations.

`research-system-live-control status` includes the most recently saved scheduling
observation, its time, source, listed IDs and each request's status/reason. The same
bounded projection is included in coordinator context for daily reports. `PENDING`
includes a missing entry or a pending review; `BLOCKED` identifies a refused gate;
`QUEUED` means existing work remains; `EXHAUSTED` means every allowed task completed.
Later criticism can change the displayed scheduling state to blocked while keeping
the original task/result and its revalidation indication. Pause, control failure or
writer contention are visible states. A changed schedule/source displays
`NOT_OBSERVED` until a tick evaluates it rather than reusing an earlier projection.

This feature does not install a timer, change resource allowances, choose new ideas,
generate scientific code, create authority decisions, install catalog entries or
activate standing operation. A reviewed supervised configuration may enable the
explicit allowlist without a timer: one authorized controller service invocation
then demonstrates selection and submission within its unchanged bounded allowance.
Any standing timer/allowance/configuration change requires the existing applicable
operator decision and exact review. Once its finite reviewed backlog is exhausted,
the worker waits for another explicitly installed and authorized task.
