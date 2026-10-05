# Saved scientific job preparation and result interpretation

The continuing-operation dispatcher uses the same underlying operations for
attributed agent selections and human steering. These helpers create no model
judgment and do not start a scientific job themselves.

`scientific_materialization.prepare_job` accepts only saved version/protocol
operation references, a saved settings artifact reference and a job name. It
reads `scientific_jobs_config` from installed controller configuration (the same
fixed protected JSON path used by the broker). The source, interpreter and
existing data roots come from that file. It observes the installed Python and
exact reviewed requirements; it installs no dependencies. A settings artifact is
an original JSON document with `schema: linux-scientific-settings/v1`, a
`settings` object, and `limits` containing positive integer `wall_seconds`,
`cpu_seconds`, `memory_bytes`, `output_bytes` and `output_files`. Each limit must
fit the installed execution ceilings. The runner receives that complete original
document through its fixed `--settings` argument.

Preparation preserves the original version core and copies actual protocol
artifacts, protocol decision/provider originals and settings into new immutable
paths in its derived workspace. The original specify/code-bundle protocol, the
full-input scientific-version protocol and the launch protocol must have the
same exact decision identity. Each individual decision being eligible does not
permit mixing versions. The launch request includes the complete job core,
original specification/settings/version and both applicable seals for the actual
author and opposing reviewer. Only the subsequent original launch decision can
permit the protected broker to capture and register it.

An actual launch decision may remain at the fixed
`state/formal-decisions/<operation>/round-1/decision.json` location. Capture
preserves its original provider receipts and transport automatically; it does not
require a human to copy or re-seal a decision into a scientific workspace.

The root broker's fixed `scientific_job_result` operation accepts only a
completion-event identity and calls
`scientific_job_results.export_result(registry, completion,
original_client=trusted_broker_originals)`. It validates the original attempt,
event, process/exit receipt, complete output inventory, captured scientific
version and actual authority. It retains original output files in place. Failed
or changed execution requires diagnosis/reconciliation and is not imported as a
successful result. Only reviewed-publication-policy-permitted text aggregates
are returned: at most 32 files, 30 KB each and 80 KB total, with the existing text
privacy guard. It checks a streaming inventory and never reads an unbounded
private output into memory. Other outputs are preserved privately.

The controller's `scientific_materialization.import_result` calls that fixed
broker operation and saves its exact reply and attributed import receipt under
`state/scientific-results/<completion>`. The reply binds actual source, job core,
scientific-version descriptor, protocol decision, original process and result
manifest, plus exact aggregate bytes. Duplicate operations verify the saved
original; partial or changed imports refuse and preserve evidence.

The status is `RESULT_BYTES_AVAILABLE_FOR_FORMAL_VALIDATION` with
`scientific_acceptance: false` and interpretation review pending. This mechanical
integrity check does not claim a generated return validator ran. No generated
scientific validator is imported as controller or root. The existing prospective
interpretation stage must receive this saved import explicitly, reason from these
original aggregates and their limitations, obtain its actual opposing review,
and record disposition and any eligible next proposal. No legacy campaign
`import_receipt.json` or prior review is manufactured for the new version.

Integration requires the shared continuing-operation dispatcher, root broker
handlers, original `stage_packet`/`stage_status` proof, source/config deployment
review and the explicit prospective interpretation input route. The focused
tests use toy local programs and synthetic provider fixtures; they are not a
patient launch, scientific conclusion, remote acceptance or activation receipt.

## Interpretation through the existing pipeline

A `prospective-research-task/v1` with mode `interpret` must include
`import_result: {operation, result_sha256}` naming one completed `IMPORT_RESULT`
operation. Prospective discussion or investigation of that same result may carry
the same reference. The task protocol must equal the original execution protocol.
The controller verifies the saved operation and import receipt, then compares the
entire imported result with a fresh read-only response from the protected broker.
Protected catalog registration supplies that exact completion to its existing
controller-identity verifier; it cannot request a model or arbitrary file.

The result reply includes up to 180 KB of exact executed specification, runner,
settings, requirements, validator and publication-policy source, all bound to the
captured job file map. It excludes the raw input manifest and private outputs.
Both interpretation roles receive those bytes and the original aggregates in
the same checked supplemental context. Unrelated legacy experiment files and
validation receipts are not substituted for the executed prospective version.

The existing author, independent reviewer and disposition sequence remains in
force. An approving interpretation review accepts only an exploratory proposal;
the receipt explicitly retains `PENDING_FORMAL_SCIENTIFIC_VALIDATION` and
`scientific_acceptance: false`. It does not claim the return validator ran.
Scientific result acceptance still needs applicable semantic validation and its
recorded authority. Negative criticism remains a negative review outcome.

Completed original recovery validates the original result and all received
context again. It may skip only the current operation-change admission check;
fresh registration and dispatch still enforce that check. Changed bytes, changed
protocol or missing protected originals refuse recovery. Historical P001 and
legacy interpretation keep their existing validated-import requirements.

An initial `protocol-proposal-task/v1` provides the separate proposal-only entry
before a protocol is eligible. The shared pipeline delegates its schema,
grounding, instructions and actual output validation to `protocol_proposals`,
and rechecks that validation during completion/recovery. Its six proposal files
never grant input access, scientific-version approval or execution. Missing
original data/literature evidence stays an explicit deferral.
