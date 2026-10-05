# Remaining hosted scientific-task adapter gap

Read-only inventory at `c165b495b330d8956ed5e4219114e5071bb2e0e7`. This
records implementation work still needed; it is not a new service or permission.

The readiness queue executes fixed metadata handlers and records their completion.
`readiness_discussion.discuss` then invokes the real campaign author/reviewer route,
but this is not yet a protected installed handler that the hosted driver can select.
The current snapshot generator includes orchestration modules and selected context
artifacts, but not `scout.py` or the unattended campaign agent profile needed by
`run_isolated_stage`. A successful source snapshot therefore does not establish
that the installed host can run the scientific pipeline.

The smallest next implementation must reuse `campaign_pipeline.execute` and its
existing source-bound stage receipts. It needs a fixed discussion/readiness handler,
an immutable source and aggregate-only attempt directory, actual separate Codex
and Claude identities, original private protocols and output validation. It must
not simply run both provider clients with a shared credential-bearing identity.

The existing campaign pipeline can use up to two author/reviewer rounds (four
model calls), while the proposed standing server turn envelope is at most three
synchronous calls. The adapter must explicitly split repair into a later eligible
admission or bound its initial round; it must not hide extra model calls within
one admission. Supervised preparation is authorized; live shared state and writer/
reset permissions remain separately held.

Acceptance must show an actual eligible completion selecting this handler, producing
a useful reviewed scientific readiness/discussion artifact, recording its outcome,
and reconciling a duplicate without model replay. Metadata inventory, a simulated
handler or an outer conversation alone does not satisfy that test. Existing passed
synthetic continuation and recovery evidence should be reused.
