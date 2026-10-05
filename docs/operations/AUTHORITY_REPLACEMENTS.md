# Explicit authority replacement after a source repair

`operation-replace` records one request beneath an existing failed operation. It
runs no model in the caller or SSH session. The next ordinary controller service
invocation can perform one fresh authority step; a later invocation can register
and submit the unchanged scientific task. The existing scheduler then runs its
normal scientific stages. Pauses, admission limits, current material review,
current change criticism and human scientific stops remain in force.

This narrow route requires a **different current installed implementation source**,
an original `AUTHORIZE_TASK` discussion selection, a conclusive exit-0 malformed
context-hash output, no sealed decision and protected proof that opposing review
never started. Timeout or ambiguous attempts, same-source corrections, already
registered/submitted scientific tasks and second replacement requests refuse.
It neither fixes the old judgment nor reuses it as an approval. The deciding model
may defer; fresh eligibility requires its normal actual independent review.

Use the source and paths shown by the current installed configuration. The
following is the supported module CLI; a deployment's convenience wrapper may
have a narrower command whitelist and must not be edited around its review pins:

```sh
PYTHONPATH="$INSTALLED_SOURCE_ROOT" /usr/bin/python3 -B -m orchestrator.handover_runtime \
  --config /etc/research-system/live-research/controller.json \
  operation-replace "$ORIGINAL_OPERATION" --human \
  --expected-source "$CURRENT_INSTALLED_SOURCE" \
  --change-request "$REVIEWED_REPAIR_REQUEST" --applied-event "$CURRENT_APPLIED_EVENT" \
  --reason 'Request fresh current-source authority after the reviewed implementation repair; preserve the invalid original.'
```

Run the human command through the authenticated root transport. It drops to the
controller identity using the existing fixed command route and records its
attribution accurately as an authenticated root transport with a declared human
initiator. Agents use the same API with their own `--submitter` actor JSON instead
of `--human`. Attribution is not an additional authority grant. The selected repair
application must be current, actually reviewed and bound to the installed source.

The response names the original operation, replacement number 1, immutable request
identity, requested-by actor, reason, current and original sources, private saved
directory, and state. Save that response. `operation-status` and normal `status`
show `linked_replacement` on the unchanged original operation. Read it after a
transport timeout before repeating the request. An exact duplicate returns the
same state; it does not start another attempt. Different arguments refuse after
the first intent. A partial intent or started step without its completion stays
`RECONCILIATION_REQUIRED`; polling does not retry a model or uncertain registration.

The same programmatic path is:

```python
from orchestrator.authority_replacements import request
saved = request(runtime, original_operation, by=actual_actor, reason=reason,
                expected_source=runtime.config['source'],
                change_request={'request_id': reviewed_request,
                                'applied_event': current_applied_event})
```

Do not invoke the authority executor directly to bypass the saved request. Do not
invoke the old operation's recovery under a substituted source. Existing recovery
and fresh-selection source checks are unchanged. The replacement keeps the exact
original task ID, scientific request, selected-by artifact and predecessor source
bindings; the task must be absent from both catalog and submission records before
the replacement starts. It receives new current-source entry, evidence and context
identities. Its full original invalid judgment, stopped failure, original provider
receipt and original authority packet are saved as evidence, together with the
exact reviewed repair chain. Both new authority roles and subsequent discussion
roles receive that content-addressed evidence, including the original limitations.

The original operation directory is never renamed or rewritten. New files live
only in `continuing-operations/<original-operation>/replacement-1` and the existing
content-addressed evidence store. A reviewed DEFER completes that linked record
without registration. An accepted eligibility decision proceeds through existing
protected registration and attributed `submit_research`, and saves their returned
links. Neither completion nor registration asserts scientific acceptance.

The installed material review must include the new module, Runtime/operation
integration, these instructions and focused tests. Keep the prior implementation
snapshot, old catalog entries and original broker source allowlist for historical
verification. A directory-presence claim or a copied receipt alone is insufficient:
the replacement reads the protected original continuation and never-started review
through the configured broker before requesting fresh authority.


## Fixed second replacement after input refusal

The explicit operation-replace request may carry --previous-request with the exact
saved replacement1 request identity. This selects replacement-2, not an open
attempt counter. A third replacement is unsupported. Existing replacement1
requests, files and status remain readable and unchanged.

The second request requires a changed installed source and a current, independently
reviewed APPLIED repair. It rechecks the original discussion, selection and
predecessors, then verifies replacement1's exact started/failure/stopped files and
protected original input refusal. The root reader supplies actual raw rc1 ended
and process originals, the exact input_too_large stderr, a single thread.started
stdout, the original packet and hashes. A timeout, answer, receipt, opposing review,
decision seal, registration, submission or active process refuses this route.
The prior admission remains consumed. The new evidence retains one complete
scientific proof plus the small refusal originals and hashes, avoiding another
copy of the full prior packet.

Both the request and ordinary continuation retain the original failed operation.
The next authority uses the new source's explicitly versioned evidence format,
fresh author and opposing review. DEFER remains terminal without registration.
Before starting authority, the installed two-role input preflight must pass.
A refusal saves preflight-failure-0.json and requires reconciliation; it does not
create a started model step or silently try another composition.

Example structure, with all values supplied from the recorded current repair:

    python3 -B -m orchestrator.handover_runtime --config <fixed-controller> operation-replace <original-operation> --previous-request <exact-first-request> --reason <recorded-reason> --expected-source <new-source> --change-request <repair-request> --applied-event <reviewed-application> --submitter <attributed-agent-json>

The request itself calls no model. Runtime advances only its ordinary eligible
step, preserving pause, human stops, independent review and accounting. A saved
replacement is implementation provenance, not a scientific result or permission
to bypass current policy. A terminal linked DEFER is visible but does not itself
create an OPERATION wake; other work must be independently eligible.

## Understanding an input refusal

An input-capacity failure means the complete message could not be submitted. It
is not a scientific rejection. The system preserves the failed request and its
accounting, and shows that saved work as requiring reconciliation. A plain-language
change request can name that operation; the applying agent supplies the exact
version and predecessor bindings through the same recorded operations.

Before a fresh eligibility call, the system measures the complete author message
and the opposing-review message with the maximum permitted judgment included.
Both must fit. The broker checks the actual final message again before dispatch.
The observed Codex bound is 1,048,576 characters; Claude uses a conservative local
bound whose provider limit remains unverified. A refusal is saved without silently
trying a different message.

The current evidence format references the full literal task evidence in the same
message instead of copying it twice. It verifies the packet hash and reconstruction
and labels that content as untrusted evidence. Historical requests keep their
original format and bytes; the new format cannot inherit their scientific approval.
