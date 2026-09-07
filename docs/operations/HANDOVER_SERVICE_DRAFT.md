# Handover service integration — not installed or activated

These units are review inputs, not proof of hosted operation. Keep the existing
synthetic controller/worker and immutable execution snapshots intact. Do not enable
these timers as an installation side effect.

The controller runs as `research-controller` without network or sudo. It can use
one local socket and its private state. The broker obtains the caller UID from
the kernel. Client requests cannot choose a command, user, directory or environment.
The proposed broker currently needs root only for its fixed `runuser` launcher,
which runs model clients as the existing separate driver/reviewer identities.
This differs from the earlier proposed non-login publisher service: it must be
reviewed and either separated or explicitly included in the final permission
packet. No new writer credential may be installed on the strength of this draft.

The socket is owned by systemd, so a broker restart preserves the listening path
without deleting an unknown socket. Broker crashes can leave a model outcome
uncertain; the controller queries saved original receipts and never equates
missing evidence with permission to retry. A timer is not evidence of recovery.

The runtime's status and operator request commands share the coordinator's state.
Pause/resume requires a root-owned request bound to the installed source and the
current control revision. Pause stops new task admission and preserves already
running work. Phone acknowledgment remains separate and cannot invoke these
controls or reset the limiter. Operator reset is a separate protected command.

Still required before installation acceptance: configuration validation, scheduled
report/event ingestion, installed human CLI testing, shared Actions provenance
collection, publication cache preparation, evidence-backed recovery and fresh
review. The live writer/admission/reset decision remains pending; 48/96 is selected
but inactive. No patient or unattended authority is conferred by these units.

Pre-launch refusal is distinct from uncertain execution. `stage_status` reports
`NOT_STARTED_RECONCILIATION_REQUIRED` when the original start marker is absent;
it does not authorize a retry. The operator reconciliation route is to inspect
the protected turn binding, stage request, process/start/end records and original
private model-work directory, then record a bounded repair decision against that
exact turn/source. Preserve all originals and any completed predecessor review.
Until a reviewed repair handler is installed, the task stays blocked and other
eligible work continues; do not edit SQLite or delete model-work directories to
force a retry. This remains a named first-handover implementation gap, not a new
scientific or permission requirement.
