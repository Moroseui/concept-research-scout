# Finite research task authority

`authorize_research_task` is an explicit delegated scientific decision for one
installed P001 `discuss` or `readiness` task. It permits bounded preparation using
the supplied evidence. It grants no patient processing, code generation or
execution, new data access, spending, publication, main merge, limiter reset,
release of a human stop, or unattended activation.

An installed entry binds the complete request, evidence bytes, source, predecessor
dispositions and applied change version. Its eligibility-file reference is
excluded from the decision core to avoid a circular hash. The existing
`scientific_decision.execute` workflow obtains an actual investigator judgment
and opposing Fable review, then records its existing decision seal. The seal is
the recorded authority disposition; no third investigator call is claimed.
Negative review leaves the original artifacts and blocks eligibility. Deferral
retains a rationale and reconsideration conditions.

The protected transport preserves original provider receipts and sessions. For
Astra, the requested model is recorded separately from the actual model reported
by the protocol. An unreported actual model remains null. Before dispatch, the
adapter retrieves the original replies through `stage_status`, compares both
artifacts and provenance, and verifies the exact sealed decision. Local records
alone cannot establish model authority.

The shared policy is version `20260910-finite-preparation-v2`; the supplied role
context is `20260910-remote-handoff-v4`. The original user direction remains
unchanged. Prior v1 decisions retain their original source and policy binding;
they acquire no new action or scope under v2. The catalog's live gates still
require the named predecessor, an unsuperseded applied change with explicit
review approval, existing admission limits and current stop controls. An
eligibility judgment is not a substitute implementation-review event.

An administrator prepares the exact finite entry and uses the fixed installed
controller configuration. Both a human control route and an agent can invoke
the same operation as the configured controller OS identity under the existing
permission boundary. Root must use that fixed identity; direct root socket
requests are refused by the broker. The operation also checks the controller UID
before creating output. The private output parent must already belong to that
controller with mode `0700`; an administrator uses the fixed
`runuser -u research-controller` route and installed source/configuration, as for
existing controls:

```text
python -m orchestrator.research_task_authority --config CONFIG --entry ENTRY --output PRIVATE_OUTPUT
```

The entry may initially name the intended eligibility path with an all-zero
digest; only its core is proposed. The operation returns the actual decision
path and digest for the administrator's immutable catalog installation. It never
installs that entry, dispatches research, or grants deployment or activation.
The source and generated configuration require their applicable review before
the operation is deployed or used.

Fresh authority uses the existing coordinator writer and admission locks. A saved
pause blocks the new admission before output is created. An admitted turn may
finish its investigator judgment, opposing review and seal while a later pause
blocks subsequent turns. Pause does not cancel an in-flight stage. The existing
broker admission identity and limits remain authoritative.

Repeating completed delivery verifies original authority without a new model
call. Recovery uses the saved original change context, even when later criticism
has arrived; fresh dispatch still applies the current change and stop gates.
Interrupted output is preserved. Use a fresh private output and
`--recover-from ORIGINAL_OUTPUT` to project the original broker replies; recovery
cannot invoke a model. Missing or contradictory originals cause a named refusal.
The saved request, judgment, opposing review, seal and transport receipts remain
available for inspection through the same private task state and change records.
