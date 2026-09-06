# Bounded hosted readiness acceptance

Run the reviewed `orchestrator.readiness_queue` from a fresh, administrator-owned,
source-pinned sparse checkout of the explicitly authorized development branch.
Acquire only that branch, depth one and no tags. No patient archive or credentials
are transferred. Preserve the existing installed worker/controller and frozen P001.

One transient systemd service runs as **research-controller**, not root. It uses
`RuntimeMaxSec=120`, `MemoryMax=512M`, `CPUQuota=100%`, `TasksMax=16`,
`KillMode=control-group`, `UMask=0077`, `NoNewPrivileges=yes`,
`PrivateNetwork=yes`, `ProtectSystem=strict`, and `ProtectHome=yes`.
Only its fresh private readiness state directory is writable. Capture stdout and
stderr there as original evidence. This is one supervised synthetic acceptance,
not a new recurring service or live admission activation.

The manifest launches a 30-second harmless primary task. The adjacent thread
executes context, P001 metadata and Phase-B metadata inventories while it waits.
Three separate gated entries remain blocked. Reconcile after completion, then
repeat and verify the event count and original artifact identities do not change.
A missing result is uncertain, not evidence permitting replay. Record actual unit,
UID, source, elapsed/resource evidence, intervals and duplicate result.

The old three goal records stay immutable. The new stage database references their
parent IDs; model authentication is not a dependency of deterministic inventories.
They remain separate from the existing synthetic execution database. No automatic
patient dispatch, result import, scientific adoption or phone reset handler exists.
