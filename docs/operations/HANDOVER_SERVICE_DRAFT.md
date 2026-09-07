# Handover service — operation and remaining activation gates

The synthetic fixture is installed and exercised; live operation remains inactive.
[Current checklist](DEPLOYMENT_CLOSEOUT_CHECKLIST.md) and
[actual completion result](HOSTED_COMPLETION_RESULT_20260907.md) distinguish installed
source from pending repairs. Preserve old receipts and immutable execution sources.

The controller runs as `research-controller` without network or sudo. The protected
broker receives the kernel peer UID and accepts fixed schema-bound operations.
Its fixed root launcher selects only the configured driver/reviewer users and
scrubbed environments. No client selects commands or users. A live writer key is
absent; the [combined privilege design](PROTECTED_WRITER_ADMISSION_DECISION.md)
requires explicit approval before installation. The scientific worker has no model
or GitHub credential.

## Supported human route

The final source supplies `/usr/local/bin/research-system-control`, an administrative
convenience wrapper over the same versioned runtime. It is installed at `9af868d47fecaf26c82c88a4d957183ea50962f5`; actual
status/pause/repeat/resume and invalid-input verification passed. Original failure
and success evidence is retained in [the final record](hosted-final-handover-20260907/human-controls.json).
After authenticated operator SSH login:

```sh
research-system-control status
research-system-control pause
research-system-control resume
```

Status is read-only and does not stop valid work. Pause/resume automatically bind
the installed source and current control revision; repeated desired state is a
no-op. Controls apply as the non-root controller. Pause blocks new admissions,
including successor dispatch, while admitted computation and original evidence
remain intact. Resume never turns on a timer, resets the limiter, authorizes a
patient job or repairs uncertain execution. JSON detail is available through the
same `python -m orchestrator.handover_runtime --config` interface without `--human`.
No agent sudo or operational phone reply is enabled. GitHub Mobile supplies checked
reports/notifications after separately gated publication configuration; the actual
phone test proved informational delivery and authenticated synthetic acknowledgment.

## Recovery and evidence

The systemd socket survives broker restart. Durable stages and original receipts
are reconciled before a new call. Actual lost-response recovery and duplicate
processing passed with zero new model calls. A controls-read failure blocks new
successor selection until repaired; final source tests cover that fault. A missing
start marker or receipt does not authorize a retry. Inspect the exact protected
turn/source, process/start/end evidence and coordinator status, then record a bounded
repair. Never delete evidence or edit SQLite to force another run. Other eligible
work can continue when only a task-specific dependency is blocked.

Original private evidence resides under protected broker/attempt directories;
controller reports are under `/var/lib/research-system/handover-controller/reports`.
Publication selects only bound report, aggregate evidence, review and disposition
assets; consoles, model protocols and credentials remain private. The current
fixture allowance is consumed, its temporary timer is stopped, and no permanent
handover timer is enabled. Ordinary deterministic executor timers remain running.

The selected 48/96 policy is inactive. Writer/reset permission, shared-state
initialization, activation verification and explicit unattended approval precede
24–48 hours of laptop-disconnected observation. Application-state sample restore
passed; provider recovery and full unattended operation remain unproven.
