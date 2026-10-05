# Finite installed research requests

The existing coordinator can now list, inspect and queue more than one installed
P001 discussion/readiness request. It preserves the original single-request route
and its saved identities. This source change does not install catalog entries,
authorize science, raise a model allowance or activate a service/timer.

Humans use the fixed authenticated administrative transport:

```sh
research-system-live-control research-list
research-system-live-control research-inspect next-discussion-v1
research-system-live-control submit-research next-discussion-v1
research-system-live-control submit-research
research-system-live-control propose research:next-discussion-v1 'Explain the remaining evidence limitation.'
```

The last command records a proposal only. The no-argument submission still means
the retained original request. Listing/inspection/submission do not call a model
or admit a turn. Pause/resume operate on the same coordinator. Queued eligible work
uses the existing Astra construction, independent Claude review and Astra
disposition stages; a finite queue eventually reports that no eligible work
remains. A daily report timer is not research task generation.

Agents call the same `Runtime.research_list`, `research_inspect` and
`submit_research` operations or the existing Runtime CLI. New entry submissions
require `submitted_by` attribution (CLI `--submitter` JSON). Actual model/session
attribution belongs there; it grants no authority. The root human wrapper supplies
`ssh-uid:0` with identity source
`authenticated_root_transport_declared_human`. This declares the human route;
SSH identity alone cannot prove who is at the keyboard. Original request proposer,
eligibility decision actor and first queue submitter remain separate saved fields.
Do not have an agent call the human wrapper to fabricate a human proposal.

An administrator's reviewed configuration may add `research_catalog` with exactly
`directory` and `legacy_source` keys. The latter contains the retained original
`source` and `source_root`, preserving its exact identity across a source upgrade.
Keep the original `research_request`, evidence and installed source present.
The private catalog directory is root-owned, controller-group-readable and not
group/world writable; each root-protected JSON filename is its task ID. At most
32 entries are read. Task IDs are lowercase letters/digits/hyphens, at most80
characters, with an initial letter/digit. No control accepts another path, source,
backend, command or environment.

Each entry has the following exact fields:

- `schema`: `installed-research-catalog-entry/v1`.
- `source`, `source_root`: the exact installed implementation.
- `request`: the existing task/evidence-file/evidence-SHA/day/initiator record.
- `eligibility`: an exact decision `path` and `sha256` reference.
- `predecessors`: at most8 exact task/source/disposition-SHA bindings, each requiring
  either `DISPOSITION_RECORDED` or `APPROVED_PROPOSAL_ONLY`.
- `change_request`: the original `request_id` and affected `applied_event`.

The canonical entry digest is included in the saved task identity and both role
contexts. Changing request code/settings, evidence, source, predecessor, change
version or decision requires a new installed task version; overwrite/removal of
an entry already used by a task produces a named reconciliation refusal. A
request ID is not a mutable pointer to the latest scientific question. The
`core(entry)` helper excludes only the later eligibility-file reference so an
authority judgment can bind its complete subject without a circular digest.

New dispatch requires the linked applied version to remain active and have its
applicable recorded review `APPROVE`; pending review and later active criticism
block it. Other change requests are not consulted by this entry gate. An exact
predecessor is checked against the original scientific pipeline and protected
broker replies. `COMPLETE` alone does not mean scientific acceptance: a negative
review cannot satisfy `APPROVED_PROPOSAL_ONLY`. An independently authorized
discussion of the criticism may require only its recorded disposition. Neither
case changes the predecessor's original review. Inspection keeps the saved result
and flags revalidation when later criticism applies.

`research_catalog.verify_eligibility(config,entry)` calls the fixed
`research_task_authority` adapter. A decision reference or declared actor cannot
unlock it: the adapter verifies the original judgment, opposing review and model
provenance, exact core/evidence/policy and protected original replies. The explicit
`authorize_research_task` action is limited to P001 discussion and readiness;
existing scientific actions are unchanged. Pending, deferred or negative outcomes
are refused. The integrated source and exact installed entry require their
applicable review and deployment before fresh catalog science can run. See
[finite task authority](FINITE_RESEARCH_AUTHORITY.md) for the shared operation,
pause semantics and original-only recovery.

Completed original tasks remain inspectable and can recover from their retained
source/workspace and protected replies, even after a later source is installed.
Historical recovery requires every original stage, verifies each original reply,
and restores completion without a new admission. Missing historical stages stay
blocked; the new implementation will not execute them under old approval. Existing
current-source recovery semantics remain unchanged. Source review and deployment
must retain old broker-readable source pins without silently granting them fresh
execution authority.
