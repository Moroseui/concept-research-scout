# Recorded change requests

A human or agent can name an idea, notebook or run and propose a repair in plain language. The request records the proposed source and selected file hashes before implementation. It does not launch work or grant authority.

For example, from the research checkout:

```sh
python -m orchestrator.change_requests submit \
  --store "$SCOUT_CHANGE_REQUEST_STORE" \
  --target campaign:isles24-pilot:P001 --human operator-name \
  --request 'Save generated decision records with owner-only permissions and preserve their bytes.' \
  --file orchestrator/scientific_authority.py \
  --scope-limit 'No scientific content, model, data or budget change'

python -m orchestrator.change_requests inspect \
  --store "$SCOUT_CHANGE_REQUEST_STORE" --target campaign:isles24-pilot:P001
```

The human identity is declared by the operator; it is not an attestation or an execution approval. Agent callers use `--actor-json` with `kind`, `family`, `model` and the actual `session_id`. Campaign submissions reuse the existing actioner request constructor. Other targets use the same request-only steering envelope and content checks.

The implementation driver uses the same Python operations to record what happened:

- `submit(...)` saves the immutable proposal, source and file versions.
- `preserve(folder, path)` retains permitted original evidence with its SHA-256.
- `record(folder, 'AUTHORIZED', actor, payload)` records the existing authority reference, rationale and applicable review policy. Existing scientific execution gates still enforce authority.
- `record(folder, 'APPLIED', actor, payload)` records the actual modification, checks and result binding. Every new application starts with review pending, even when an older application was approved.
- `record(folder, 'REVIEW', actor, payload)` binds an actual review artifact and verdict to one exact application event. Criticism names affected results. A later disposition records the driver's response.

The `record` CLI accepts the same attributed actor and payload manifests as these Python calls; humans need not edit saved records. Inspection shows the same proposal, authority, applied versions, checks and pending/outcome state that the driver uses. Identical recordings reuse their originals. Conflicting or damaged evidence fails verification. No recording runs code or a model.

Use `context(store, task=None)` in existing task/report inputs, and `context_text(store, task=None)` in both role contexts. With `SCOUT_CHANGE_REQUEST_STORE` configured, the shared scientific stage context supplies this state prospectively and records what each stage actually received. `operations_report.finalize(..., task_state={'change_requests': context(store)})` binds the same state into the existing daily report. Pending application events form the review worklist; they never silently become approval. Original context receipts remain unchanged when a later request arrives.

Low-impact reversible repairs may proceed with checks and deferred review when existing policy permits. Material scientific changes still need their applicable review before affected execution or acceptance. This module is bookkeeping for the existing workflow and does not replace its gates, schedule a second pipeline, or make saved private evidence publishable.