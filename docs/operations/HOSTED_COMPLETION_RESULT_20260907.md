# A completion caused the system to execute its successor

The bounded test passed on the purchased Linux host. A new synthetic predecessor
completed, the persistent non-root coordinator invoked Astra, a fresh Claude
review assessed the evidence, and Astra selected the configured successor. The
existing Linux worker completed it; a second report/review/response closed its
completion without selecting another job. This is infrastructure evidence, not a
patient experiment or permission for unattended operation.

| Question | Measured result |
|---|---|
| Did completion trigger useful execution? | Yes: two new jobs completed; one successor submission, recorded once. |
| Did real models run through the system? | Six calls: two Astra continuations, two fresh Claude reviews, two Astra responses. |
| Were source identities preserved? | Reporting/coordinator `a0795e69ed6c225fe353d438b5558f481340fe81`; executor `6b555075fcf553994ecac8e368f4676cbdffdc56`. |
| Did execution and separate retrieval verify? | Both artifacts matched `776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800`; original console hashes and coordinator/model receipts verified. |
| Resource measurements | Predecessor 10.245 s (including a deliberate 10 s wait), 0.173 CPU s; successor 0.240 s, 0.147 CPU s. Each recorded 19,200 KiB peak RSS. Six model calls totalled 270.675 s; this sum is not whole-campaign elapsed time. |
| Final state | Both events PROCESSED; both reports/reviews/dispositions COMPLETE; fixture admission count 3 including the older retained turn. Temporary polling timer stopped. |

[Primary receipt](hosted-completion-20260907/receipt.json) contains job/attempt
identities, six model receipts, usage fields, source/document hashes and observed
controller confinement. Astra was explicitly requested as `gpt-6-astra`; its CLI
protocol does not independently report the resolved model. Claude reported
`claude-fable-5`. Unavailable cost and intervention measurements are not invented.
[Preservation receipt](hosted-completion-20260907/preservation.json) identifies the
private archive containing original protocols, consoles, state and setup evidence;
those originals are retained, not replaced by hashes or published.

## Review findings and response

The [first review](hosted-completion-20260907/50-handover-a0795e6-review.md) and
[second review](hosted-completion-20260907/51-handover-a0795e6-review.md) found a
control-path defect: failed reading of the operator inbox blocked model admission
but did not block successor submission using the previous pause state. They
explicitly distinguished this handover blocker from the permitted supervised
successor. Astra [selected only that successor](hosted-completion-20260907/50-handover-a0795e6-disposition.md)
and [recorded the final corrective task](hosted-completion-20260907/51-handover-a0795e6-disposition.md).

The local repair gates both submission paths on control-channel success. A real
synthetic-child fixture verifies that failed control reads preserve completed
review/selection evidence and hold INTENT at zero submission attempts; repairing
the channel permits exactly one submission without new model calls. Fresh source
review and installation of this correction remain pending. The successful hosted
snapshot is preserved unchanged.

The reviews also lacked existing recovery, backup and human-control receipts.
That is an evidence-supply defect, not evidence those earlier tests failed. The
collector now selects those primary receipts directly; completion packets also
include the same bounded coordinator census as scheduled reports. Separate
research queues are not falsely described as freshly observed. Historical receipts
remain explicitly historical. No 24–48 hour disconnected proof is claimed.

These fresh hosted Claude sessions are separate cross-family reviewers operated
by the system; they are not the independent main-merge desk. Their original wording
and Astra's attributed responses remain unchanged. Required main review and
operator approval remain separate.

## Next action and limits

Finish the control repair/delivery review, install the consumed-fixture update
without increasing its allowance, and assemble the concrete writer/reset/admission
permission packet. The broader prediction charter, 047b lifecycle and evidence
propagation tasks remain queued. Setup has produced no P001 score or scientific
result; the Wednesday scientific path still requires its own charter/adoption,
input/backend and patient-launch decisions. Cleanup, reserved cases, main merges,
new spending and unattended activation remain outside this test.
