# Correcting a published system report

A correcting report is a new immutable primary report. Its `amendment_of` link identifies the preserved original. It receives its own normal continuation, fresh opposing review, disposition, publication and notification. Existing companion reviews remain unchanged. A completed nightly review does not automatically submit an amendment.

Use the installed `Runtime.enqueue_report(..., amendment_of=original_report_id)` API and then `runtime.q.submit(binding)`. The first call saves the report and task inputs and **returns a binding**; the second submits that binding to the ordinary coordinator. Calling `operations_report.finalize` alone does not submit a coordinator task. An amendment accepts only the ordinary report trigger, with no scientific task ID or execution proposal.

This API does not authorize a repair, deploy changed source, resume controls, admit models or start services. A material presentation change must first have its applicable original review and deployment receipt. Use the fixed installed controller configuration and controller UID997, with the existing private state and admission limits. The existing service performs the subsequent work independently of the initiating SSH session.

## Prepare the exact recorded input

Before writing runtime state, record the correction purpose, affected report, actual submitting actor/transport, applicable change request and applied version through the existing change workflow. Retain a bounded private input with `source`, `change_request`, `applied_event`, `submitted_by`, `amendment_of`, `day`, `receipts`, `task_state`, and `reviewer_evidence`. Its source must be the exact installed reviewed implementation. `submitted_by` records the real initiator; it does not authenticate scientific authority.

Use the actual saved receipt collection and a captured coordinator context, with observation times. Do not make execution receipts from coordinator rows or write a replacement report body. The generator renders the primary report. Preserve the original correction review and qualified disposition as literal `reviewer_evidence`, together with their saved identities. Put the recorded correction request and transport identity in permitted `task_state` metadata so both role inputs and the saved report have attributable origin. Do not imply a new observation when retaining old evidence.

Freeze those inputs in the durable administrative intent before calling the API. The following is the existing shared API sequence, run as the controller identity after the installed-source and input checks. `intent` is that already checked, retained JSON object, not a fresh model request or an alternate configuration. Preserve the bound input file and its SHA in the administrative receipt.

```python
import json
from pathlib import Path
from orchestrator.handover_runtime import Runtime, configuration
from orchestrator.handover_coordinator import encoded
from orchestrator.operations_report import immutable, pin
from orchestrator.remote_supervisor import lock

config = configuration(Path('/etc/research-system/live-research/controller.json'))
runtime = Runtime(config)  # Enforces the configured controller identity/source.
assert intent['source'] == config['source']
pin(intent['change_request'], 64)
pin(intent['applied_event'], 64)
pin(intent['amendment_of'], 64)
assert intent['task_state']['correction_request'] == intent['change_request']
assert intent['task_state']['correction_applied_event'] == intent['applied_event']
assert intent['task_state']['correction_submitted_by'] == intent['submitted_by']
saved = runtime.state / ('report-amendment-' + intent['change_request'] + '.binding.json')
with lock(runtime.state / 'branch.lock'), lock(runtime.state / 'admission.lock'):
    binding = runtime.enqueue_report(
        intent['day'], intent['receipts'], intent['task_state'],
        reviewer_evidence=intent['reviewer_evidence'],
        amendment_of=intent['amendment_of'],
    )
    immutable(saved, encoded(binding))  # Save identity before any submission.
    submission = runtime.q.submit(binding)
```

This is the initial submission sequence, not a blind replay script. Preserve `saved`, the returned task ID, the immutable task packet/report references, and the actual `q.submit` result. The packet binds `amendment_of`; the new report links the old primary. The existing queue validates the task binding and refuses conflicts. Inspect the new ID through `research-system-live-control status` or the existing JSON status route.

## Reconcile an interrupted submission

If the saved binding exists, read that exact binding and its saved task inputs, check them against the retained intent, and call `runtime.q.submit(binding)` under the same locks. Do **not** call `enqueue_report` again: current change context may have advanced. Repeating `q.submit` with the same valid binding returns a duplicate result without a second task. If there is only a partial report/task preparation with no saved binding, preserve all files and reconcile that prefix before another construction; do not silently create a second identity.

Once queued, the existing controller service uses the normal pause, deployment and admission checks, publishes the finalized new identity, and requests fresh stages. Bookkeeping attaches the review only when its source/report hash matches that new identity; an old report review cannot satisfy it. The ordinary reviewed delivery publishes the new companions and notifies under the new report's dedup key. No new notification operation or recursive nightly-review trigger is needed.

Success requires the new task's actual completion, bookkeeping, published successor identity and notification receipt. A saved binding or queued row alone proves none of those outcomes. Preserve both old and new receipts, and leave disconnected-observation duration and unrelated scientific acceptance claims to their own evidence.
