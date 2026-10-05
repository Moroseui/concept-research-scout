# Prepare a bounded Linux research service

`deploy/research-system/prepare_live_research.py` prepares the existing live broker
and a controller for one explicitly bounded scientific desk task. It writes only
private proposals. It does not install a service, launch a model, enable a timer,
create credentials, initialize/reset a ledger or grant unattended authority.

Supply the reconciled live broker configuration, previous controller identity,
exact reviewed source, and a recorded research request. The request names the
existing campaign discussion/readiness operation, stable task identity, exact
private evidence digest, date and attributed initiator. The source snapshot and
evidence remain separate. Keep raw notebook outputs and withheld reviewer text
private; a prepared aggregate is not a new scientific result.

The generated broker uses the existing ledger, writer and live turn directory.
Its supervised allowance is one task with three fixed model stages. Installation
must first confirm that this live directory still has no started turn, so the
proposal cannot quietly replace a consumed allowance. The old synthetic fixture,
controller state, completed model records and all original configuration remain
preserved. Source identity and resource/permission changes need actual review.

The current model-disabled publisher unit hides model homes and allows 512MiB.
The proposal reuses the already exercised model service's settings: separate
research-driver/research-reviewer identities, server-local credential refresh,
4GiB broker memory, two CPU equivalents and 128 tasks. The controller keeps its
512MiB/one CPU/32 task bounds and cannot use the network. Only the protected broker
can reach the providers. Its model commands and OS identities remain fixed in code.

The controller uses `/var/lib/research-system/handover-live-controller`; its
configuration and private evidence live under `/etc/research-system/live-research`.
Evidence is root-owned, group-readable by the existing controller group, with no
group write or world access. Change requests use a controller-owned private store.
The generated research controller is a systemd oneshot, with no timer. Once
explicitly submitted and started, PID1 owns it independently of the initiating
SSH connection. Original model receipts and the shared coordinator govern recovery;
a missing result must be reconciled before a retry.

Source/configuration proposals and local checks do not demonstrate server behavior.
Before claiming a bounded disconnected run, retain the actual submitted task,
installed source/unit/configuration hashes, service identity, original model calls,
opposing review, disposition, and post-disconnection/recovery observations. The
scientific task's artifacts remain private. Standing scheduling, report delivery,
phone controls and unattended activation require their own completed checks and
recorded decisions; this proposal does not silently enable them.
