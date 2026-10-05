# P001 transparent setup route — prepared 8 September 2026

Status: **engineering proposal; not executed or source-reviewed as a new route**.
This concerns setup on the already selected CPU Colab runtime. It grants no
patient launch, archive extraction or scientific acceptance. The existing setup
packet at `9b843d5164d6e4e89f49098acd6d2744d95b8e0d` received source-review APPROVE;
that review does not prove setup ran or cover a different transport implementation.

## What actually stopped

Three original attempts remain privately preserved under
`resume-20260908/p001-runtime-setup-{execution,reconciled,authority-clarified}-9b843d51`.
Their native worker protocols and final responses are the evidence; a worker's
narrative alone is not execution proof.

1. **Execution attempt:** the Session opened its Colab connection, read cell
   structure without prior outputs, and successfully appended one CPU-check cell.
   It submitted no `run_code_cell` calls. The next `add_code_cell` returned an
   unknown-tool error. The worker retried that add after refreshing discovery,
   then a read-only `get_cells` also returned unknown-tool. Those attempts are
   retained; the extra add attempt did not follow the packet's stop-on-first-error
   instruction. Only the CPU-cell append has a successful tool response. Source
   readback for that appended cell was never completed. Protocol SHA-256:
   `f19081748c4b692d1fbcb4d7a0d91deaa5b9c859272d4a7a0177e6701873ec0d`.
2. **Reconciled attempt:** zero tool calls. The worker declined the supplied
   nested `exec(compile(...))` and redirected-output presentation, interpreted the
   restrictions as preventing observation, and requested authorization/runtime
   clarification. Protocol SHA-256:
   `d82b5d7e14e4ee931d85f599f6b4ef5b0032f624d5040d5119933dd12e34e762`.
3. **Authority-clarified attempt:** zero tool calls. Despite the supplied approved
   scope and output clarification, the worker again declined, citing opaque live
   execution and its inability to independently establish authority from the
   packet. Protocol SHA-256:
   `a1ca18cccc07690d3cc82a4a531dddcaf6c215596c523ea42983d1654aeb3656`.

No setup execution is established by any attempt. The two refusals were model
responses, not a Colab permission-denied response. Stop sending persuasion variants.
Preserve the refusals and the notebook append; reconcile actual current state before
any further execution. The proposed change addresses the substantive visibility
and deterministic execution concerns.

## Fixed transparent setup

Retain the existing request identity, runtime fingerprint, source root and exclusive
setup root. Do not create a new identity or directory to evade an existing intent.
The last independent observation was request `p001-runtime-20260908-v3`, fingerprint
`d3db37e0c1e0ae7aae7e00e11edaa438624c2c2456b3245fa51e1dcdad335b6c`; it is historical
input to a fresh guard, not a claim that the runtime remains unchanged.

The runtime actions remain narrowly defined:

1. Reconcile the existing connection and unexecuted cell using source-only notebook
   reads. Then obtain current CPU/runtime/Drive/archive metadata, source state,
   process and prediction-output observations. Match the original fingerprint and
   expected metadata. Any uncertainty or existing setup intent requires recovery,
   not a repeated setup. Do not read pre-existing notebook outputs.
2. Record the same exclusive setup intent before mutation. Present the actual
   readable source-acquisition statements from frozen notebook cell 1: initialize
   the fixed `/content/scout-pilot-d6a1184b4378` checkout if absent, fetch exact
   `d6a1184b4378e849213fd887a6f7b103fb1a64d5`, detach at that pin, and verify HEAD and
   cleanliness. No source substitution, existing-checkout reset or branch push.
3. Present the actual readable dependency statements from frozen notebook cell 3:
   install its exact requirements (`numpy==2.3.3`, `nibabel==5.3.2`) and check the
   existing review artifact. Reuse the separately reviewed conditional 7-Zip
   installation statements only when `7z` is absent. No preflight or prediction.
4. Recheck source/runtime conditions and use the existing fresh-child environment
   probe to verify default-interpreter package imports, versions, origins,
   distribution inventory and 7-Zip version. This proves the observed child
   environment, not future immutability or scientific execution.

The readable cells should contain the operative statements directly. Avoid nested
escaped `exec(compile(...))` payloads and process-wide stdout/stderr redirection.
Preserve original stdout, stderr and failures in the same private logs, while
returning bounded, inspectable per-step outcomes: operation identity, exact source
hash, return code, elapsed time, and the concrete postcondition checked. Every new
execution result must be inspected. Missing output, a failed command or mismatched
postcondition stops advancement. A bounded diagnostic excerpt, when needed, requires
credential filtering; never expose raw private logs merely to make progress visible.

The frozen notebook cells are unchanged historical sources. Any supplementary
logging/guard presentation has its own executed-source hash and new review; do not
label altered cells as byte-identical originals. The prior synthetic Colab receipt
already records that ordinary subprocess fd output can be missing from notebook
outputs, so silent completion alone is inadequate evidence. Reuse explicit child
and source postconditions in addition to actual execution results.

## Minimal deterministic MCP transport

A small versioned dispatcher is appropriate for these fixed engineering operations
if the existing MCP registration supports an ordinary authenticated client. Its
availability has not been established by this assessment. It must preserve meaningful
oversight through readable inputs, original response evidence and checked outcomes;
merely sending the same opaque packet through another client is insufficient.

The dispatcher should have one bound request and a fixed state machine, with no
model-generated commands or general-purpose execution input. Reuse the existing
approved connection/authentication. Permit only initialization/tool discovery,
one connection opening when needed, source-only `get_cells`, exact cell append,
and one ordered `run_code_cell` for each newly bound stage. Maintain one live MCP
client session across dynamic tool discovery; an unknown tool or lost connection
must stop, not trigger automatic reconnect, append replay or execution retry.
Do not edit, move, delete or execute pre-existing cells unless a separately reviewed
recovery explicitly establishes their exact original binding and nonexecution.

Persist intent before each potentially mutating request and retain the actual MCP
request/response IDs, arguments, source readback, execution results and errors
privately. A lost response is uncertain, even if the request might have succeeded.
Inspect/recover that same operation before any resend. Native MCP evidence must
remain honestly labeled; do not manufacture Claude `assistant`/`user` events to
make a different client appear to have used the old Session validator.

## Reuse and necessary review

Reuse `orchestrator/p001_runtime_setup.py` for frozen source extraction, prior
receipt/request binding, `check_observation`, `claim_setup`, `child_environment`
and `validate_environment`. Reuse the fixed observation schema and collector from
`orchestrator/p001_runtime_intake.py`. Preserve the source/readback/run-order and
error checks established by `orchestrator/colab_patient.py`; factor or adapt them
for native MCP exchanges without weakening them. Keep `orchestrator/colab_worker.py`
and its frozen capture implementation unchanged as historical reviewed evidence.

A fresh source review must cover the transparent cell renderer, the actual MCP
client and configuration boundary, native transcript verification, original-log
handling and recovery behavior. Focused synthetic tests should demonstrate wrong
runtime refusal; preservation of an existing intent/source/output; lost append/run
response without retry; changed readback; duplicate or unbound run; tool loss;
subprocess failure; missing/truncated results; dependency mismatch; and no extra
or arbitrary stage beyond the exact reviewed packet. Verify the exact bound source and all applicable existing
review receipts before an actual setup attempt. Source review and synthetic tests
remain distinct from the eventual real Colab receipt.

## Remaining time and operator dependency

Allow **0.5–1 engineering hour initially** for the fixed readable renderer, minimal
client/receipt adapter and focused checks, provided the existing MCP registration
is directly usable. Confirm that interface first. If it is available only through
the model harness, report that concrete limitation before expanding scope; do not
spend an open-ended interval building another browser bridge. Fresh source review
is additional model/observation time. Actual Git/package installation and environment
observation are additional runtime, dependent on Colab and network response; no
experiment-runtime estimate is implied.

No repeated Drive grant, OAuth consent or SSH unlock is requested by this proposal.
The existing setup authorization remains the governing scope; no new grant or
unreviewed execution is inferred. An operator action becomes necessary if the
existing browser connection actually requires sign-in/attachment, Drive is no
longer mounted, or the approved runtime was replaced and its new binding needs a
scoped decision. A real permission denial or missing authority cannot be overridden
by the dispatcher. A frozen readable-notebook setup presentation is the fallback
for an operator-controlled session if direct MCP access is unavailable, after its
same guards and resulting evidence are reviewed. The separate exact prediction
launch decision still follows verified setup/environment evidence.