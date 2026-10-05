# Independent Linux scientific jobs

`orchestrator.linux_scientific_jobs` executes a registered, reviewed scientific
Python version through an independent systemd instance. It reuses `job_store`
jobs, events and inbox records. It preserves the synthetic supervisor and Colab
interfaces. Exit zero makes evidence available for formal validation and
interpretation; it is never scientific acceptance.

The implementation is separate from a scientific version. The installed source
stays pinned. A protected capture overlays exact reviewed scientific artifacts
onto unchanged installed support files in a new private immutable snapshot.
Later proposal edits cannot replace the executed version. The snapshot copies no
Git object database, credentials or patient payloads and performs no network I/O.

## Protected integration

The existing broker must select these operations itself after authenticating its
controller peer, checking current human stops, applicable linked change review,
predecessor disposition, and pause/resource controls. Consumers cannot provide a
callable, shell, source checkout, filesystem destination or alternate policy.
The broker supplies its internal read-only `original_client`, which verifies
actual saved provider outputs. A fabricated assertion of approval is insufficient.

```python
registry = linux_scientific_jobs.Registry(installed_job_config)
registry.register_scientific(core, original_launch_decision,
                             original_client=broker_original_client)
# Inside the existing live controls/admission guard:
dispatch = registry.dispatch(core['job_id'], original_client=broker_original_client)
# Only REGISTERED permits starting this exact unit, with systemctl --no-block.
# INTENT or STARTED_OR_UNCERTAIN requires reconciliation, not another attempt.
events = registry.observe()  # no model and no process launch
```

`register_scientific` selects only
`config.proposals / core.proposal_id / 'workspace'`. Configure that parent as the
existing `state/scientific-versions` derived-workspace directory. Preserve all
original formal task workspaces. The root broker automatically captures the
reviewed version; an operator does not install a new checkout for each successor.
Only the selected experiment, protocol and explicit review/authority artifacts
may differ from the installed source. Other review inputs, including references
absent from a sparse release, must match that source's Git blob identities.

The core binds the job identity, implementation source, scientific-version
descriptor, complete scientific file map, specification, settings, exact
requirements, interpreter version/binary/dependency fingerprint, data manifest,
protocol proof, arguments, and finite limits. Arguments invoke only the captured
campaign `run.py` through the configured Python interpreter, without a shell.
Only `@output`, `@input` and `@settings` receive fixed installed paths. The input
manifest is `linux-scientific-inputs/v1` with an approved `root` and a complete
`files` map of relative paths to SHA-256 values. Its root must be in the installed
existing-data allowlist; each declared file is checked before execution. The
reviewed runner/protocol must enforce its declared selection and exposure scope.
This adapter grants no new dataset access or patient transfer.

Three genuine decisions are distinct: `authorize_protocol`, the full-input
`approve_scientific_version`, and `launch_linux_job`. `decision_request(core)`
returns the launch action, job subject, exact core/source/experiment/spec/code
bindings, and transition `REVIEWED_EXECUTION_PROPOSAL` to `LINUX_JOB_ELIGIBLE`.
`scientific_versions.verify_authority` checks the complete prospective P002/P003
scientific version against both original model legs. This new adapter refuses
P001 mutation; frozen P001 keeps its existing execution and review paths. The protocol
seal binds actual partition registry, exposure history, literature and methodology
review, and any prior protocol. A scope boolean is never a protocol approval.

The scientific-version descriptor names `scientific-version.json` and
`scientific-authority/<version_id>/round-1/decision.json`. Include all exact
judgment/review/provenance/provider receipts and the parent authority transport in
the job's file map. Capture also preserves original launch and protocol decision
rounds, provider receipts and transports. Missing or changed inputs refuse.

## Deployment and operation

Install the module, unit template and the reviewed scientific-version/policy
adapters together. `render_unit(config)` binds only the fixed source/output paths
in `deploy/research-system/research-system-scientific-job@.service.in`.
There is no timer or automatic activation in this change. The existing controller
can poll through its protected broker every 60 seconds and continue other work.

The root-owned `/etc/research-system/linux-scientific-jobs.json` has exactly:
`source`, `source_root`, `python`, `requests`, `outputs`, `database`, `snapshots`,
`proposals`, `worker_uid`, `worker_gid`, `maximum_parallel`, and `input_roots`.
Pin actual existing `research-worker` and `research-runtime` identities. Use
private root-managed request/snapshot/output parent directories outside the
controller and broker state trees; workers are denied those state trees. Give
the worker group read/traverse access to configuration, requests and snapshots.
Each output directory is explicitly worker-owned mode 0700, including under
umask 0077. Root-owned database/state remain broker-only. The fixed interpreter
may be a protected existing virtual-environment symlink; no package installation
occurs during a job. Requirements should include all transitive dependencies
needed by the reviewed execution environment.

An exact root-owned request follows the durable database intent. The protected
caller starts only `research-system-scientific-job@<attempt>.service`; an SSH
session does not own that process. Each instance runs as the existing unprivileged
worker with no credentials or network, a private writable output directory,
systemd memory/CPU/process ceilings, and tighter requested process limits.
Multiple registered instances may overlap up to the installed parallel ceiling.
The installed ceiling must fit the existing server's memory, disk and CPU budget.

The worker saves boot/PID/start identity before preflight or child launch. It then
saves the actual child identity, arguments/environment binding, private console,
result manifest, and outcome. A crash after intent or start never authorizes a
new attempt. Repeated completed worker invocations return the original outcome.
`Restart=no` and `KillMode=control-group` retain uncertainty rather than relaunching
an interrupted experiment. Original failed/partial captures and attempts remain
available for explicit recorded repair or a newly approved job identity.

Timeout and output-limit failures preserve original files and produce diagnosis
events. Output polling can overshoot the aggregate threshold between polls; the
per-file OS limit and systemd ceilings remain in force. An oversized or unsafe
output set is marked `OUTPUT_RECONCILIATION_REQUIRED`; no truncated result is
accepted. External termination before a terminal receipt remains uncertain and
requires process/output reconciliation.

`observe()` validates original receipts and result hashes, then records one
deterministic `ANALYSIS_AVAILABLE` event in the existing event store. It includes
the actual source/core/runtime settings, authority and result-manifest identity,
plus original process/exit hashes. The formal task adapter must reference this
verified event and its original files for validation/interpretation, independently
review and dispose of that analysis, and record any successor. Later corruption
blocks completion ingestion while preserving the previous event for correction.
No polling, process exit, fixture test, or pending review becomes acceptance.

The focused tests run small local fixtures with explicitly mocked authority;
they do not represent patient execution, real model approval, deployed systemd
behavior or the required disconnected observation. Those gates must be checked
on the reviewed integrated source and actual installed configuration.
