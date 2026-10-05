# Reviewed continuing operations

`orchestrator.continuing_operations` connects the existing investigator pipeline to saved system operations. An investigator chooses a next operation in `selection.json`; its independent review and recorded disposition must accept that exact original selection. Choosing an operation is a proposal. The operation's applicable scientific authority, application, registration and execution remain separate steps.

The optional checked configuration is `continuing_operations: {enabled: true}`. Absence disables discovery and advancement. It supplies no seed task, resets no allowance and grants no authority. Status and discovery never call a model. Human and agent controls use the same saved operations and identity checks.

The existing `campaign_pipeline` investigate stage may select this exact successor shape:

```json
{
  "schema": "continuing-operation/v1",
  "operation_id": "a-new-reviewed-version-name",
  "kind": "APPROVE_VERSION",
  "inputs": {
    "materialization": {"operation": "64-hex", "result_sha256": "64-hex"},
    "protocol": {"operation": "64-hex", "result_sha256": "64-hex"}
  }
}
```

`contract()` defines each exact input shape and `instructions()` supplies the same contract to the roles. Other kinds prepare task eligibility, authorize a protocol, materialize a scientific version, authorize/register/dispatch a Linux job, or import a protected completed result. Inputs are original artifact references or completed operation references. Models cannot supply commands, callbacks, implementation paths, permissions or arbitrary formal authority requests. Fixed constructors derive each scientific decision request from checked saved evidence.

Existing campaign-task successors continue to work: discovery prepares an `AUTHORIZE_TASK` operation from the actual selection. The first step runs the existing deciding agent and opposing reviewer through `scientific_decision`; the second installs the immutable eligible catalog entry through the protected broker and invokes the same attributed submission operation used by humans. Submission still does not admit or execute the scientific task.

## Runtime integration

The shared Runtime calls `discover(runtime)`, `advance(runtime)` and `status(config)`. Call `advance` outside Runtime's `branch.lock`: the existing authority adapter acquires that writer/admission boundary itself. The operation coordinator holds one separate operation lock and performs at most one saved step per call. Ordinary Runtime admission, pause, source, current-change, human-stop, original-model and resource checks remain effective.

The shared selection parser calls `validate_selection(task, successor)` lazily for this schema and appends `instructions()` to the investigator prompt. Both roles receive the exact `status(config)` projection under `packet.continuing_context.continuing_operations`; protected scientific completion events go under `packet.continuing_context.scientific_completions`. This separate immutable snapshot leaves the catalog's approved `reviewer_evidence` unchanged. A referenced result absent from the selecting roles' original snapshot is refused. A successor's `import_result` must also name a checked completed `IMPORT_RESULT` in that snapshot. The next task's authority receives the original snapshot as `prior_continuing_context` in its newly prepared evidence. These projections are private system context, not a public daily report.

A `protocol-proposal-task/v1` successor uses the same task-authority and registration path. Separate `AUTHORIZE_PROTOCOL` preparation requires the six originals from one actual reviewed `protocol_proposal` task. A deferred bundle, missing original evidence or mixed proposal version cannot reach that decision. The proposal helper does not grant scientific authority.

The fixed protected routes are `register_scientific_job`, `dispatch_scientific_job`, `scientific_job_status`, `observe_scientific_jobs`, `scientific_job_result`, and existing task registration. Root-protected `research_controller_config` and `scientific_jobs_config` select installed configuration; request bodies do not. The scientific-version verifier additionally uses the read-only `stage_packet` route, checking the original protected packet SHA before its fields. Neither packet nor status reads establish review by themselves: both actual original model replies must independently verify.

The Linux helpers are `scientific_materialization.materialize`, `attach_review`, and its forwarding operations `prepare_job` and `import_result`. Version, protocol, settings, input and environment hashes remain explicit. The generated code's original full-input review is attached as an unchanged copy; no historical investigator or legacy review receipt is synthesized.

## Inspecting and recovering saved work

Each operation has an immutable request, preparation, step intents and completion receipts under `state/continuing-operations/<identity>`. A completed result reference contains its operation identity and the exact result-file SHA. An unchanged operation version selected again reuses the same work. Changing its inputs requires a new version name. The queue has no hardcoded total mission capacity and no exhaustion-based scientific permission.

Status distinguishes queued steps, completion, reversible deferral and an interrupted attempt needing reconciliation. A deferral cannot reach registration or execution. A saved attempt without a completion is never automatically retried. `recover(runtime, identity)` can recover complete original authority replies into a fresh private projection using only `stage_status`; it forbids new admission/model operations. Later criticism remains visible and is checked before a dependent next step. Uncertain job starts and partial artifact copies remain with their original fixed adapter's reconciliation path, preserving every original.

`read_operation_result(..., current_review=False)` is limited to the internal recovery of already completed work. It still verifies the immutable request, original source, exact final step and result-file SHA, while the completed-task caller also checks the original protected broker response. Fresh use defaults to `current_review=True`; model operation inputs cannot select this flag. Later criticism blocks fresh dependent work without rewriting its historical evidence.

An imported Linux result remains original evidence with `scientific_acceptance: false`. The current import explicitly marks semantic validation pending. Prospective interpretation must preserve that status and its exact completed-job/version/protocol references; importing it does not create a legacy validated import or scientific acceptance. The unchanged historical P001 workflow retains its original evidence and gates.
