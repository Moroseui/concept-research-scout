# CLI restart reconciliation — 7 September 2026 UTC

Branch `astra/infrastructure-milestone-record`, HEAD
`e478ad0844e771d37e80a4cb1eda9e4f42ebc02f`. The interrupted draft was preserved:
runtime report evidence, broker mode reporting, trusted reviewer evidence collection,
their tests, and the new supervised service acceptance harness. No reset or retry
was performed. The harness had not been installed or executed remotely.

At approximately 03:08 UTC, SSH succeeded using the existing agent. No remote
Claude/Codex process or package installation was present. The original controller
and worker polling timers remained active; their one-shot services were inactive
with successful exit status. Five existing attempts had five outcomes. The Colab
dependency remained blocked without an attempt. Three historical PENDING_AUTH wake
labels remain unresolved; they do not establish current authentication failure or
authorize replay. Previously processed wakes and original outcomes were preserved.

The failed closeout-02 and closeout-03 units match the already recorded SQLite
snapshot and context-storage failures in CLOSEOUT_ATTEMPT_FAILURE_20260906.json and
CLOSEOUT_CONTEXT_FAILURE_20260906.json. They were not restarted or cleared.
The active source symlink still points to `6b555075fcf553994ecac8e368f4676cbdffdc56`.
Neither new handover broker nor controller configuration exists on the server.
Original private diagnostic output remains in the local resume-inspect and
runtime-status files; no raw model console was exposed.

The sandbox initially rejected SSH configuration ownership. The existing bounded
collector succeeded outside that sandbox; no host configuration was changed and
no key unlock was necessary. This was distinct from expired SSH authentication.

Continuation: finish testing and review of the supervised service harness, then
prepare a fresh immutable installation for bounded acceptance. Its recovery phase
must never invoke a model; live admission state must be refused. New harness tests
cover these refusals and observed resource prerequisites. An initial test mocked
the process-wide UID and interfered with pytest temporary-directory ownership;
the fixture now isolates that mock to the harness. All 17 focused tests pass.

The prediction-charter, 047b processing and evidence-propagation tasks remain queued
under their existing dependencies. No patient launch, live limiter/writer grant,
unattended activation, main merge, cleanup or new spending occurred. Full service
acceptance and fresh review of this uncommitted draft remain pending.
