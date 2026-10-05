# Current policy and recorded changes on Linux

The hosted model adapter uses the same checked scientific policy as the local
campaign workflows. `configs/scientific-operating-context.json` binds the current
documents and two complementary roles. The original scientific grant is unchanged.
The snapshot builder includes those dependencies; a missing or altered bound file
refuses the invocation. Historical immutable snapshots keep their original context.

Every new hosted invocation saves its complete policy, selected role, source and
task-packet identity in `<stage>.operating-context.json`. Its execution receipt
binds that file and the actual supplied prompt. A document edit or a passing local
test is not proof of deployment: inspect these original server artifacts for both
roles before claiming current policy delivery.

To include the existing change-request records, the administrator sets the
root-owned runtime configuration's `change_request_store` to a task-scoped private
store owned by the controller identity. Use the existing
`python -m orchestrator.change_requests --help` submit/record/context operations;
no hand-editing of history is needed. The human and agent routes use this same
store and validators. Caller attribution is preserved, not treated as a permission
grant. Configuration alone does not authorize a scientific change or activation.

At task/report creation the controller validates and freezes the full projection
in the private task packet. Both roles receive it, including applied versions,
pending reviews and criticism of affected results. Daily reports expose only the
request identities, application states and review states. Proposals and retained
evidence remain private. A later review appears in subsequent tasks and reports;
existing prompts and result bindings remain immutable. Keep stores scoped to the
affected saved work within the existing 20KB projection bound.

Local checks cover portable policy dependencies, actual envelope construction for
both roles, refusal of missing/changed policy and preservation of a pending repair
when later criticism changes the next report/task identity. Exact source review,
installation and real server delivery remain separate evidence.
