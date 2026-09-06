# Supervised hosted cycle: actual execution and remaining gaps

The server completed one bounded three-call cycle from the existing, previously
unprocessed completion of synthetic job `30-linux-next`. This exercised recovered
event handling, not a new scientific dispatch or a new timer-triggered model turn.
The actual synthetic attempt is `fee07efbb4ca4d13affed829b8da5ba9` at source
`6b555075fcf553994ecac8e368f4676cbdffdc56`; the operations adapter ran at
`ba079f88bad9d186613687e105dd6f2b551e45e5` in a separate root-owned snapshot.
The installed execution symlink was preserved.

Astra continuation, fresh Claude review and Astra disposition all completed through
`orchestrator.hosted_cycle` and the existing report queue. These were real hosted
subscription calls, not fixtures or replay. Codex requested exactly `gpt-6-astra`,
with no configured fallback; the captured protocol does not independently report
a resolved model identity. Claude's assistant protocol identifies `claude-fable-5`.
Authentication status was checked privately for both accounts. Original prompts,
protocols, stderr, report database and outputs remain private on the server and
in the retrieved private evidence archive (SHA-256
`59015f11f359f252806b2297ac38e75c6a26df688e234c0a53d36818c49fd17b`).
Hashes verify retrieved originals; they do not replace those originals.

Readable artifacts:

- [System report](hosted-cycle-20260906/39ce1a9fd5c4cbabbbfc3cdd220f1cd59c752c4a8fe823879c1b96b0f3d63203.md)
- [Fresh hosted Claude review](hosted-cycle-20260906/review.md)
- [Astra response and next action](hosted-cycle-20260906/disposition.md)
- [Evidence amendment](hosted-cycle-20260906/source-tool-evidence.json)
- [Bounded cycle completion](hosted-cycle-20260906/complete.json)

Claude found the receipt chain internally consistent and the report faithful, but
correctly withheld full operational acceptance. Genuine gaps include a missing
failed-review reconciliation command, source/context completeness, coarse worker
failure reasons and directory durability in the underlying report module. The
review also identified unresolved wake status; a separate evidence-verified,
non-dispatching reconciliation route passed focused Claude review and was applied
to the hosted completed event. A repeat returned duplicate=true with zero model
calls and zero job dispatches; see the wake-reconciliation receipt. No full deployment approval is claimed.

The system-recorded Astra response agrees with the acceptance gaps and requests
a reconciled evidence packet. The deterministic source/tool amendment performs
that next action in part: worker, report generator and smoke source bytes are
identical across execution/report pins; the captured Claude init event reports
`tools: []`, `mcp_servers: []`, and `permissionMode: dontAsk`. This contradicts the
reviewer's speculation that effective tools were present. The original review
is preserved; the amendment is not a fresh review or approval.

Hosted duplicate delivery returned the existing completion with three stages
before/after and zero new model calls. Prior hosted restart/event, sandbox,
19-file application backup/restore and synthetic 48/96 tests remain valid. They
are not provider backup recovery, live limiter activation, phone delivery, or
24–48 hours unattended operation. The deterministic timers remain separate from
model admission. The adapter is an explicitly invoked, supervised setup route,
not a deployed standing driver or a substitute for protected writer/reset design.

All three research tasks are now registered and included in a hosted report.
Original task bindings were preserved. No charter adoption, 047 interpretation,
patient transfer/launch, reserved-cohort access, cleanup, main merge, or new paid
resource occurred. Drive/Colab remains queued outside Linux acceptance.

Usage and elapsed measurements are in per-stage receipts. Claude reports a
$1.075564 cost-equivalent for this hosted review; this is SDK-reported usage
accounting on the authenticated subscription route, not evidence of a new API
charge. Codex dollar measurements and operator intervention time are unavailable.
Implementation reviews incurred separate existing-subscription usage, recorded
in their attributed receipts. Job counts are not dollar limits.

Remaining work before live operation: reviewed failed-call recovery, full protected
admission/writer/reset integration, live authority approval, actual phone delivery
and authenticated response, scheduled report review, model/quota fault acceptance,
resolved model identity evidence where available, provider recovery and the
24–48 hour disconnected observation. The notification-only App proposal is
prepared; credentials and permissions have not been installed or expanded.
