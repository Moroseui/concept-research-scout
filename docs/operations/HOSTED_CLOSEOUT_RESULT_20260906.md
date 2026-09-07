# Bounded hosted closeout result — 6 September 2026

**The supervised synthetic chain completed:** a new Linux job finished, an actual
Astra call selected its single predeclared eligible successor, the system executed
that successor once, generated a report, obtained a fresh Claude review and saved
Astra's disposition. This is a constrained execution handoff demonstration, not
open-ended scientific prioritization or unattended acceptance.

Reporting/continuation source: `e7bff17940629479c939d6ae9b9f181dc6af93f9`.
Preserved worker/controller execution source:
`6b555075fcf553994ecac8e368f4676cbdffdc56`. CI for the reporting pin passed,
[run 34057593134](https://github.com/Moroseui/concept-research-scout/actions/runs/34057593134).
No new-version worker deployment or patient execution is claimed.

| Stage | Actual evidence |
| --- | --- |
| New predecessor | `40-closeout-trigger`, attempt `7573e0bba1c34724bdd0f660fdbc0e75`, COMPLETE; 0.262 s wall, 0.184 s CPU, 19,200 KiB peak RSS. |
| Astra selection | Real call explicitly requested `gpt-6-astra`; [selection](hosted-closeout-20260906/selection.json) matches the predeclared successor. 7.604 s. |
| Successor | `41-closeout-followup`, attempt `10010973a12b491793b65f44f238fc53`, COMPLETE; 0.187 s wall, 0.134 s CPU, 19,200 KiB peak RSS. |
| System report | [Pinned report](hosted-closeout-20260906/ab3b6f03899e26f086de69ec8f0d0b9c6e79f5dc167a644915c6c4a58f06bfe4.md), SHA-256 `ab3b6f03899e26f086de69ec8f0d0b9c6e79f5dc167a644915c6c4a58f06bfe4`. |
| Fresh review | Actual `claude-fable-5`, 103.906 s; [original review](hosted-closeout-20260906/review.md). |
| Astra response | Real call explicitly requested `gpt-6-astra`, 16.220 s; [system disposition](hosted-closeout-20260906/disposition.md). |
| Wake closure | Reviewed validator ran as the controller identity against a private verified copy; first processed the trigger, repeat was duplicate, both with zero dispatch/model calls. [Receipt](hosted-closeout-20260906/wake-reconciliation.json). |

Both job artifacts match SHA-256
`776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800`.
Original consoles and all three model input/output hashes were separately verified.
Eighty-eight original files, failed journals and implementation-review records were
preserved and verified in the existing private evidence archive. Its manifest hash
is `543e81240ef445a7746084df612a4786c7132ad13e925e0027dfd6deef2beb08`.
Originals remain on the host too; hashes are not substitutes for those originals.
Only checked aggregate artifacts and execution metadata are published.

## Failures and review findings

The first setup attempt completed the predecessor, then failed reading a serialized
WAL snapshot before any model call. The second failed storing the expanded source
packet through the 100 KB public-summary writer, also before any model call. Their
[WAL](CLOSEOUT_ATTEMPT_FAILURE_20260906.json) and
[context](CLOSEOUT_CONTEXT_FAILURE_20260906.json) receipts remain separate.
Repairs use a consistent controller-UID row snapshot and bounded owner-only private
context storage. Public-summary limits remain unchanged. The predecessor was never
rerun. Source-only Fable reviews and revisions are
[attributed separately](CLOSEOUT_IMPLEMENTATION_REVIEWS_20260906.json).

Fresh hosted Claude review supports the internally consistent synthetic chain but
withholds broader operational acceptance. It identifies missing directory fsync
in the preserved worker, incomplete unit hardening, missing wake context and
unexercised newer worker/recovery behavior. Astra's system disposition agrees with
those limits while qualifying two inferences: inactive oneshot services do not
prove manual execution, and a capability bounding ceiling does not establish
actual effective privileges. The reviewed fixture allowance has separate
implementation-review receipts in this branch; those receipts were absent from the
hosted reviewer packet. Preserve that context omission as a follow-up finding,
not as evidence that the reviews never happened.

The [source/tool amendment](hosted-closeout-20260906/source-tool-evidence.json)
reuses the system evidence-preparation script. Claude's effective tools/MCP lists
were empty. Astra's requested exact model and no-fallback command are recorded;
the protocol does not independently report its resolved model. The transient
setup unit finished; existing deterministic timers remain. The successor's wake
is intentionally pending another bounded admission, not authority to loop.
[Later journal evidence](hosted-closeout-20260906/service-invocation-amendment.json)
binds the successor's recorded PID to `research-system-worker.service`, and both
timers are active/waiting. This addresses the missing invocation evidence without
rewriting the original review or claiming new worker-code acceptance.
Worker status fields saying `model_execution:false` describe the credential-free
worker, not these separately receipted model calls.

## Phone and resource evidence

The operator confirmed GitHub Mobile delivery after enabling notifications.
The App verified the operator's exact issue-4 acknowledgment; a repeat was
idempotent. [Phone receipt](NOTIFICATION_APP_IDENTITY_20260906.json).
This was supervised API polling. Automatic polling and operational replies are
not enabled, and the first blocked-phone test remains unconfirmed delivery.

The three hosted model calls took 127.730 s combined. Codex receipts report 50,805
and 52,761 input tokens, and 55 and 318 output tokens respectively. Claude reports
69,678 cache-creation input tokens, 1 input token and 7,156 output tokens, with
CLI-reported cost $1.798594. That is a provider-reported usage estimate, not evidence
of an additional invoice on the subscription. Codex dollar cost is unavailable.
No new credentials beyond the approved notification App, provisioning or paid
fallback occurred. Total engineering/intervention time was not reliably measured;
review wall times and per-call usage are retained rather than reconstructed.

## Remaining finite work

[The checklist](DEPLOYMENT_CLOSEOUT_CHECKLIST.md) separates demonstrated behavior
from protected admission/writer/reset, automatic recovery, recurring reports,
provider restore and 24–48 hour unattended observation. The
[permission design](PROTECTED_WRITER_ADMISSION_DECISION.md) remains proposed;
48/96 activation and operational phone replies remain gated.

The prediction-charter, 047b reconciliation/import and cross-charter evidence tasks
remain in the migrated queue with their scientific/evidence dependencies. P001 is
unexecuted; no patient result or scientific improvement is claimed. The next
system-recorded action is a bounded plan covering deployment compatibility,
v2 receipt tests, service invocation evidence, durability and wake recovery.
