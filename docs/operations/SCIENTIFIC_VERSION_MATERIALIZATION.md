# Materializing a prospective scientific version

`orchestrator.scientific_materialization.materialize` copies previously reviewed
formal proposal, specification and code-bundle outputs into a new derived
workspace. It constructs no scientific content, runs no proposed code, calls no
model and supplies no full-version approval. Original completed tasks and frozen
P001 remain intact. This operation supports prospective P002/P003 versions.

The existing controller calls the same operation for an attributed human or agent:

```python
receipt = materialize(
    controller_config, experiment='P002', version_id=version_name,
    proposals=three_saved_proposal_descriptors,
    protocol_decision_sha256=actual_protocol_decision_sha,
    parent_version_sha256=prior_version_sha_or_none,
    original_client=protected_original_reply_client,
    by=actual_recorded_human_or_agent_actor,
)
```

The calling route selects fixed controller configuration and enforces its
existing pause/steering permissions. The operation requires the configured
non-root controller UID. The `by` identity records who applied the copy; it is
not an execution grant or an invented human attestation.

Each descriptor contains exactly `task`, its original `source`, `mode`,
`packet_sha256` and the exact `artifacts` hash map. There must be one reviewed
`propose`, one `specify` and one `code_bundle` task. The operation reuses
`continuing_research.read_reference` and the scientific-version verifier's
original-provider checks. Changed original packets, declined review, missing or
extra output files, wrong hashes, or unavailable provider originals refuse before
a new workspace is created. Original proposal source identities may be historical;
they are preserved, while the new full-version review binds the current source.

The artifact map comes from `scientific_versions.artifact_targets`: exact
`SPEC.proposed.md`, runner, validator, requirements, publication policy and tests
become their experiment paths without rewriting their bytes. The original idea
and every source output remain referenced by task, packet and artifact hashes.
`scientific-origin.json` records that lineage and protocol decision. No legacy
`investigator_decision.json`, `review.json` or adoption receipt is synthesized.

The new directory is always
`state/scientific-versions/<scientific_version_sha256>/workspace`. It contains
unchanged installed support, the copied scientific artifacts, and canonical
`scientific-version.json`. Required support is read from the pinned installed
source with implicit fetching disabled. A sparse installation must include the
finite common scientific-review support set; unavailable bytes produce a named
refusal rather than an invented file or laptop dependency.

The private original-byte writer deliberately preserves source encoding and
uses exclusive durable files. It does not route source through a publication
formatter. Generated artifacts retain the existing reference/content guard;
publication scanners and permissions are unchanged. Intent precedes copying.
Identical completed materialization reuses the original; a partial or changed
version is retained for reconciliation and never overwritten.

The receipt records all workspace hashes, exact original-to-applied file mappings,
actual applier, provider provenance, and `PROSPECTIVE_VERSION_PENDING_FULL_REVIEW`.
The next operation uses `scientific_versions.decision_request` with the actual
protocol descriptor, then the existing formal scientific-decision transport for
author and independent review. Only its genuine `approve_scientific_version`
seal can satisfy protected capture. Linux execution additionally requires the
separate exact `launch_linux_job` decision and current policy/resource/stop gates.

The scientific runner interface is
`--data-root @input --output-dir @output --settings @settings`; only the registered
worker substitutes those paths. Aggregate outputs and the validator use the
existing campaign bundle format. Materialization compiles Python syntax without
importing or executing it; scientific correctness, resource suitability, protocol
compliance and full-input review remain explicit subsequent workflow stages.
# Attaching the actual full-input review

`attach_review(config, scientific_version_sha256=..., decision_path=...,
original_client=..., by=...)` serves the existing controller operation dispatcher.
It resolves the materialization from its saved digest and accepts only an actual
decision below the fixed `state/formal-decisions` directory. It copies the
original decision, both provider receipts, descriptor-named judgment/review and
provenance, and authority transport unchanged into the version's fixed
`scientific-authority/<version_id>` subtree. It never creates a new seal.

The actual original-provider verifier runs before copying; the full version
verifier checks that both roles received all bound files before a completed
attachment receipt is written. Deferred decisions refuse. A partially copied
attachment is preserved for explicit reconciliation. Completed duplicate calls
verify and reuse the original copy. The result descriptor is used by protected
job capture; attaching a review executes no science and accepts no results.
