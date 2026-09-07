# First remote handover — current acceptance checklist

Updated 7 September 2026. This checklist supersedes older present-tense setup
statements; the original dated receipts and Git history remain evidence. It is
acceptance accounting, not activation or scientific authority. The canonical
operating goals remain [REMOTE_OPERATING_DIRECTION.md](REMOTE_OPERATING_DIRECTION.md).

| Essential | Implemented and verified | Remaining |
|---|---|---|
| Linux execution and continuation | Immutable executor `6b555075fcf553994ecac8e368f4676cbdffdc56`; actual successful/failed synthetic jobs, blocked Colab yielding to Linux, resource and original-console evidence. Earlier `e7bff17` cycle actually selected and executed a successor. | Passed at `a0795e6`: a new completion caused one eligible successor execution, followed by its own report/review/disposition. Preserve both attempts; no repetition required. |
| Non-root protected service | Installed `9af868d47fecaf26c82c88a4d957183ea50962f5`, retaining the actual `a0795e6` and `6863968` execution snapshots; three actual Astra → Claude → Astra cycles, with distinct identities, observed resource limits and original protocols. | Final repairs reviewed at `ca8f989`, `eb40b95`, and `9af868d`; idle source update, actual short human controls and one non-root tick passed. No allowance increase. |
| Recovery and duplicate handling | Actual idle broker restart and lost-response recovery completed with **zero new model calls** and one total fixture admission. Unit tests cover idempotent successor submission after a lost response, pause, capped failures and stable first-observation evidence. | Final completion selection/bookkeeping passed, once per event. Hosted review found a controls-read failure could leave successor admission using stale pause state; the repair is tested, approved and installed. Actual prior reviews/dispositions were preserved. Uncertain starts stay blocked; neither missing receipts nor NOT_VISIBLE authorize a replay. |
| Shared admission and protected reset | CAS ledger, Actions provenance collector/waiter, server identities, 48/96 warning/halt/UTC rollover/reset tests. Genuine human-controls review at `cb2019f`; generated workflows preserve inactive policy behavior. | Protected writer/reset permission approval, one shared live-state initialization, hosted activation verification. No live limiter ref/key is installed. Main's workflow update requires its separate merge approval. |
| Publication | Existing controlled branch publisher; exact-history checks; actual hosted protected-cache intake and unsafe intermediate rejection at `386cde2`. Credentials absent from driver and scientific worker. | Reviewed-report delivery uses the same candidate/publisher route; local tests and fresh source review passed, source installed. Actual credentialed hosted publication remains untested until its grant. Live writer grant is separate. Repository-wide credentials can bypass application checks; post-push CI is only additional detection. |
| Scheduled reports and fresh review | Explicit schedule/daily dedup, immutable reports, actual fresh Claude reviews and Astra dispositions, current coordinator metadata and versioned goals/directive. | Checked delivery integration and source reviews passed. Final installed evidence is in the closing review packet; actual scheduled/credentialed operation remains separately gated. No permanent handover timer is enabled. Reporting time remains proposed, not selected. |
| Human operation | Actual hosted status/pause/resume, repeat, stale and conflicting-request tests passed through shared coordinator state. Main's human Actions controls remain available. Actual GitHub Mobile delivery and authenticated synthetic ACK passed. | Short status/pause/resume wrapper is installed and actually passed, including repeated pause and invalid input; original failed PATH test preserved. Phone comments do not authorize operational controls or reset. |
| Backup | Actual application restore verified 57 files, two consistent SQLite databases and retained model evidence, without launching anything. | Provider-side backup/restore and account-security checks remain unverified; do not repeat the application proof without a material change. |
| Unattended observation | Ordinary deterministic Linux timers survive SSH; real bounded remote model cycles are proven. | **24–48 hours laptop-disconnected operation is not proven.** Requires the completed permission packet, initialized shared state, activation verification and separate unattended approval. |

Primary current evidence:

- [Hosted service evidence](hosted-service-acceptance-20260907/receipt.json),
  [human controls](hosted-service-acceptance-20260907/human-controls.json),
  [backup recovery](hosted-service-acceptance-20260907/backup-recovery.json), and
  [protected intake](hosted-service-acceptance-20260907/protected-intake.json).
- [Approved completion bridge review](HANDOVER_COMPLETION_BRIDGE_REVIEW_20260907.json).
  The subsequent broader fixture review timed out at 600 seconds **without a
  verdict**; [its failure record](HANDOVER_COMPLETION_FIXTURE_REVIEW_TIMEOUT_20260907.json)
  preserves that distinction. The [focused review](HANDOVER_COMPLETION_FIXTURE_REVIEW_20260907.json) approved the bounded fixture, which subsequently passed actual hosted execution. Final source and path-repair reviews approved; [installed controls/service evidence](hosted-final-handover-20260907/service.json) is preserved separately. These are
  author-operated reviews, not independent main-merge desk approval.
- [Permission design](PROTECTED_WRITER_ADMISSION_DECISION.md), still proposed.

## Active setup and limits

The installed fixture has consumed all **three** allowed turns (nine model-stage
calls in total). Its broker is idle; original deterministic controller/worker timers
remain active. Both new jobs and their report/review/disposition cycles are COMPLETE.
The temporary completion timer was stopped after verification. No permanent handover
timer or patient job is running. Historical failed units and original private evidence
remain preserved. See the [actual completion result](HOSTED_COMPLETION_RESULT_20260907.md).

Current local follow-up work also prepares checked report delivery. Without a
protected publication configuration, completed reports are recorded PRIVATE_ONLY;
this does not turn a missing writer grant into a model failure or an extra review.
The delivery candidate preserves original report/review/disposition bytes and
uses one branch lock. A lost publication response checks the exact remote commit;
it does not create a replacement commit.

## Preserved scientific queue and Wednesday path

The prediction-charter/adoption task, 047b evidence/lifecycle task and cross-charter
findings-propagation task remain in the migrated server queue and
[queued task record](QUEUED_SCIENTIFIC_TASKS_20260906.json). The broader context/intake
proposal remains queued and is not a prerequisite for this first handover.
Authentication was demonstrated; older PENDING_AUTH labels are historical records,
not a reason to repeat sign-in or execution.

P001 remains **unexecuted**, with no accepted result. The archive has a historical
verified Drive preservation receipt, not a fresh live check in this setup batch.
Prediction-charter/adoption ratification, input/backend review and a separate
patient launch decision remain the scientific critical path. P001 does not depend
on accepting 047. The 99 cases are exploratory; the reserved 49 remain untouched.
047 cleanup, scientific landing, console/exclusion evidence, main merges and new
spending retain their separate gates.

## Remaining estimate and observation start

The authorized implementation and installed synthetic verification are complete.
Source reviews approved the repairs; current installed evidence is retained for
the final closing review. Publication and CI identities belong in the final
milestone report rather than being inferred from local tests. The next
configuration/activation batch is separately gated: allow roughly **2–4 engineering
hours after decisions and credential setup**, followed by the separately approved
**24–48 hour observation**. Provider/account issues can add time; this is an estimate,
not an enlarged spending or scientific grant.

Observation can begin only after final implementation/review, approval of the
concrete writer/reset and server-admission design, shared-state initialization,
hosted activation verification and explicit unattended approval. Status/report
links remain phone-readable through GitHub. The demonstrated intervention route
is authenticated SSH status/pause/resume; phone ACK is not a pause, launch, reset
or scientific approval. Any proposed operational phone extension must appear
explicitly in the permission packet before activation.

Final installed evidence and readable status example: [hosted-final-handover-20260907](hosted-final-handover-20260907/human-status-example.md). The failed first status invocation is retained privately and explained in [path repair](HANDOVER_CONTROL_PATH_REPAIR_20260907.md).
