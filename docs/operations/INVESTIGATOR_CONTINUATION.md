# Investigator continuation

An installed investigator template keeps the selected research charter active after a normal scientific task finishes. The controller records why another investigation is needed, obtains a new Astra eligibility judgment and opposing Claude review through `scientific_decision`, then registers and submits the exact task through the existing catalog. The investigator itself uses the existing `campaign_pipeline` author, reviewer and disposition stages. A proposed successor still needs its own applicable authority and review.

The template is a controller-service request, not a model judgment. Its saved initiator is `investigator_wakes.service(config)`; provider receipts separately identify the actual eligibility author, reviewer and investigator. An unreported actual provider model remains unreported. A sealed decision is the recorded authority disposition and does not imply a third eligibility model call.

## Protected configuration

The existing root-owned controller configuration may contain this optional object. Absence or null disables new investigator discovery. Enabling it does not itself authorize deployment, activation or science.

```json
{
  "investigator": {
    "template": {
      "schema": "investigator-template/v1",
      "template_id": "current-charter-v1",
      "experiment": "P002",
      "request": "Choose a useful next formal action for the selected charter using the supplied original evidence.",
      "evidence_file": "/etc/research-system/live-research/report-evidence.json",
      "evidence_sha256": "EXACT_FILE_SHA256",
      "references": [],
      "change_request": {"request_id": "EXACT_REQUEST_SHA256", "applied_event": "EXACT_REVIEWED_APPLICATION_SHA256"}
    },
    "template_sha256": "EXACT_CANONICAL_TEMPLATE_SHA256"
  }
}
```

This is a schema illustration, not an installable configuration or grant. Use `handover_coordinator.digest(template)` for the template pin: SHA256 of `json.dumps(template, sort_keys=True) + '\n'`. The evidence pin hashes the exact file bytes. Evidence must contain the selected charter and available scientific context; a server health summary alone is insufficient. References must identify existing saved task artifacts. Root configuration, source review and the linked applied-change review remain required.

The generated `investigator-task/v1` has the ordinary task fields plus `template_sha256`, `wake_sha256` and `purpose`. Its task ID is `investigator-<wake SHA256>`, `mode` is `investigate`, and `selected_by` is null. The protected adapter regenerates the task, evidence, day, initiator and predecessors and compares them to the entry. The eligibility decision binds the template explicitly in addition to the existing task/core bindings. Existing five-binding decisions retain their original meaning; changing a template, task or source cannot reuse its old decision.

## What causes another investigation

The fixed reader recognizes these saved facts:

- The current source and template have no initial investigator reservation.
- A normal scientific task has all three original stage replies and its recorded disposition, including an independently negative review.
- A completed `AUTHORIZE_PROTOCOL`, `MATERIALIZE_VERSION`, `APPROVE_VERSION` or `IMPORT_RESULT` operation has the applicable original selection, decision or result proof.
- An independent Linux job has an original completed result, ready for subsequent formal analysis.
- A current authenticated plain-language proposal has been recorded through the existing Issue 6 steering intake. The fixed reader checks its attestation and saved request identity; a comment, acknowledgement or claimed permission alone is insufficient.
- A normal scientific task is blocked and the broker preserves an ended attempt without a validated stage receipt. The reader checks the original packet, start/end records and artifact hashes while the model writer is idle. Its scientific outcome stays unknown.

Every event is reserved once in the existing protected state namespace before eligibility. Reservation is per event, so overlapping batches and repeated observations cannot create duplicate investigations. Each controller poll selects at most one fresh event. Polling, reservation and inspection invoke no model. Actual eligibility and investigator stages consume the existing admissions and resource limits.

Investigator completion and failure cannot wake another investigator directly. A model cannot select an `investigate` successor, even with a new name. `AUTHORIZE_TASK` and `LAUNCH_JOB` completion are also excluded because their normal task or job provides the subsequent evidence. No new event means no new model call. A recorded deferral remains dormant until independent evidence or an authenticated recorded proposal arrives.

A transport-failure wake has `purpose=FAILURE_DIAGNOSIS`. Its checked selection may only defer or propose a new ordinary `discuss` task. It cannot retry the original task, select a launch or claim scientific success or failure. A started process without an original end record requires reconciliation and does not wake this path. Failed Linux job outcomes remain visible in the existing job status; this adapter currently accepts completed job results, not an inferred result from a failed job.

## Evidence and review

Both roles receive the exact template evidence and verified event context. Task references come from checked original artifact inventories. Fresh operation and job metadata stay in the separately bound `packet.continuing_context`; the approved catalog evidence is not silently rewritten.

A prospective successor may use only the existing task protocol or an exact eligible protocol from a completed `AUTHORIZE_PROTOCOL` operation supplied in that investigator's saved context. The original decision is checked again. An old or unavailable protocol is listed as blocked context and cannot be selected; it does not prevent discussion of independent evidence. New literature, cohorts, partition use, code, execution and acceptance retain their existing separate gates.

An edited steering proposal has a new recorded identity. An earlier superseded proposal cannot authorize fresh eligibility or registration. Completed recovery uses its saved original packet, preserving what both models actually saw. Later criticism remains visible and gates affected new work; pending review never becomes approval through polling.

## Inspecting and recovering work

The existing human status includes investigator state; `research-list` and `research-inspect` expose registered work. An authenticated new plain-language Issue 6 proposal can request substantive reconsideration after a deferral. The same saved task and change records supply later driver, reviewer and report context. Existing pause/resume controls apply: pause blocks new admissions, while an already admitted task can finish its opposing review and disposition. A durable halt still requires the recorded operator reset route.

The controller module also provides `investigator-status` and `investigator-recover <wake SHA256>`. Invoke it from the installed source with the exact existing controller configuration; its root transport drops to the configured controller UID before accessing private state. Do not run scientific Python as root or hand-edit saved records. The existing wrapper's `status` remains usable; adding these named module commands to a wrapper is a separate reviewed installation choice.

Each private `state/investigator-wakes/<wake SHA256>/` preserves the root wake, prospective entry, authority-started intent, authority outcome and submission receipt. The latest observation includes bounded blocked reasons for inspection and reporting. Incomplete folders remain reconciliation-required and are preserved. Unrelated recorded operations needing reconciliation do not prevent an eligible investigator from advancing.

`investigator-recover` can reconstruct eligibility only from original protected replies into a fresh projection. It cannot start a missing provider stage. An uncertain authority attempt is never retried automatically. A repeated exact registration/submission reuses the existing immutable entry and coordinator identity. Historical source-bound wake records are retained for inspection and do not execute under the new source.

## Verification and deployment boundary

Focused tests cover exact template binding, actual decision serialization with synthetic provider replies, both campaign roles and original-only recovery, per-event dedup, deferral and steering edits, preserved transport failure, and the fixed verifier's real subprocess/JSON-line pipe. Synthetic fixtures are not scientific approvals. The pipe test runs as one local user; the actual root-to-controller UID transition still requires the reviewed deployment check. Source review, installed policy/role proof and the real autonomous continuation demonstration remain separate requirements before declaring the handoff ready.
