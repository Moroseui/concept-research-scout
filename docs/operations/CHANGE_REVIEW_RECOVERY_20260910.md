# Preserve criticism and inspect growing change history

A later approval of the same applied version no longer erases an earlier request
for changes. An applied repair can explicitly name `supersedes_applied_events`;
the system checks that every identity belongs to this request's earlier applied
events. The repair starts pending review. Its approval applies to that version,
while the original criticism and affected results remain in the saved history.
Superseding code does not revalidate historical scientific results.

When full change context exceeds 20 KB, the shared model/report operation supplies
a bounded summary. Unresolved criticism takes priority, and omitted request counts
and review states are explicit. A summary is never approval or sufficient evidence
for accepting an affected result. Text checks still cover omitted history. Private
records and evidence are preserved; no proposal or event is rewritten.

Humans and agents inspect the same store without editing records:

```sh
python -m orchestrator.change_requests inspect --store /path/to/private/changes
python -m orchestrator.change_requests inspect --store /path/to/private/changes --index
python -m orchestrator.change_requests inspect --store /path/to/private/changes --request-id REQUEST_ID
```

The last command verifies and returns the full proposal, event chain and evidence
bindings. Models receiving a summary must obtain the relevant full record before
accepting work that depends on omitted criticism. Public operational reports show
only change identities, states and omission warnings; proposal details stay private.

This repair addresses the early opposing direction review. Implementation checks
do not constitute an opposing review or permission to deploy or activate.
