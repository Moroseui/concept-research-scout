# First remote CPU milestone: supervised synthetic cycle

This implementation uses the existing Store tables/immutable job registration
and adds Linux attempt and wake records without changing the frozen P001
coordinator. It accepts only `synthetic_success` or `synthetic_failure` and at most
16 registered fixtures in this bootstrap store. No patient or arbitrary shell job
is accepted. Compatible Linux work proceeds when a Colab fixture is blocked.

The exact payload and separate execute/retrieve implementation are reused from
`campaigns/isles24-pilot/colab/smoke.py`. A worker process captures original stdout
and stderr in a private attempt directory, verifies actual retrieval, and writes
source/request/artifact/console identities and measured elapsed/CPU/peak child-RSS
metadata. Peak RSS is the worker invocation's child-process high-water mark,
including Git preflight, not a cgroup-level scientific memory measurement.

Controller and worker are separate non-root service identities; source and service
configuration are administrator-owned. Workers cannot access model homes or write
controller state. Driver/reviewer receive no GitHub credential. The publisher
identity is uncredentialed. Deployment acquires only the explicit code/synthetic
sparse paths from the published source pin, not the patient/result directories.
Systemd adds filesystem isolation, no network for either synthetic service,
no privilege escalation, memory/CPU/task/time caps and control-group termination.

One controller lock and one worker lock serialize activity. Persisted request
recovery does not generate a second attempt. Existing attempt directories are
never rerun, and duplicate completion identities never create duplicate events
or imports. An expired attempt without a receipt becomes AMBIGUOUS/BLOCKED, never
proof that no process ran. Original PID/boot/start metadata and output evidence
remain for reconciliation. No automatic retry of uncertain execution is enabled.

Successful and failed completions create durable wakes marked PENDING_AUTH with
CODEX_AUTH_AND_BOUNDED_TURN_REQUIRED. This is a concrete continuation path, **not
proof that a remote Astra session processed them**. Model dispatch is not enabled
by the deterministic timers; it needs remote sign-in and the applicable bounded
turn/admission gate. Live standing authority and 48/96 activation remain pending.
No claim of a deployed full driver, phone delivery or overnight acceptance follows
from the synthetic services alone.

The deterministic report module creates immutable readable reports and separately
hashed permitted primary receipt JSON, queues a fresh review, and prevents recursive
review/disposition triggering. Queue attachments require a trusted adapter to
verify actual Claude execution; hash matching is not reviewer authentication.
The current CLI intentionally does not fabricate a completed model review.
The nightly schedule and automated review transport remain unactivated dependencies.

Application backup freezes controller/worker access, uses SQLite backup, retains
original synthetic outputs/consoles and verifies a restored sample. This proves
only that application sample, not DigitalOcean weekly backup status, account
security, provider restore or retention. No backup product is purchased here.

Host validation must separately record: actual sparse source pin, role ownership,
fixed services/timers, disconnected-SSH job continuation, independent progress,
original failure, duplicate/restart recovery, pending model wakes, report queue,
backup/restore hashes and boundary refusals. Local tests are supporting evidence,
not substitutes for these deployed checks. A closed SSH connection is not the
operator's 24–48-hour laptop-disconnected acceptance period.

The next setup batch is the versioned install_release.py at an exact reviewed
commit. It installs a pinned official Node 22 binary with its published SHA256
(the initial Ubuntu Node 18 did not meet Claude's package engine requirement),
root-owned sparse source and fixed synthetic units. Firewall allows SSH only after
non-root operator key login was verified; root key access remains available.
No agent gets sudo. No model key, OAuth token, SSH private key or patient archive
is copied to the server. Original bootstrap/account-inspection logs stay private.

First hosted startup at `6b555075fcf553994ecac8e368f4676cbdffdc56` exposed a
missing sparse-checkout input: `.gitignore`, blob
`f545437ebc93eb974d8dd7090b19e79121fd80ba`. Git status tried to lazy-fetch it
inside the read-only, network-isolated services and refused. All four jobs stayed
READY; no attempt started. The bounded repair hydrates only that tracked ignore
file at the same source pin and verifies cleanliness as the controller. It does
not resubmit jobs or change their source bindings. Future installs include the
ignore file explicitly. Original startup errors remain private evidence.
