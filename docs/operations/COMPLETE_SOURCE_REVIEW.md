# Complete source review within a bounded model context

The ordinary deployment gate still accepts one complete, source-bound review.
Use the optional two-part profile when a complete input exceeds the provider's
context limit. It requires two source reviews and a final integration review.
Byte coverage does not make this equivalent to one reviewer holding every source
file at once. The final reviewer must challenge the interfaces between parts and
may require more evidence or refuse approval.

These preparation/check operations never install code, start a service or model,
activate research, or grant publication authority. Independent review of changes
to this gate remains necessary before relying on it. Existing human stops,
historical ruling requirements and activation decisions remain separate.

## Freeze one exact proposal

Start with a clean exact source and its verified archive. Add review_plan_file to
the existing research-deployment-preparation/v1 input. It names a private JSON
plan with exactly these fields:

- schema: two-part-deployment-source-review/v1.
- source and archive_sha256: the exact implementation and archive.
- shared_context_sha256: the complete original Claude role context hash.
- required_files: the named SHA256 map returned by coverage_requirements(files)[0].
- reference_files: the five fixed REFERENCE_ONLY_FILES paths and current hashes.
- parts: exactly a and b, each a complete filename-to-SHA256 assignment.
- integration: the complete filename-to-SHA256 assignment for the final call.
- shared_evidence_sha256: the nonempty unique list of original criticism and
  common evidence that all three calls must receive verbatim.

Required deployed coverage is derived from archive and policy bytes. Both service
templates are required in this profile. Assignments may overlap and must cover
every required deployed name and all five reference names. Both parts require
full common control code, full scout.py and current policy. Final integration
requires the fixed control/authority/runtime/installer/reporting boundary files,
full scout.py and current policy. Extra archive files may be assigned explicitly.
Reference-only files are checked against the clean local Git source and retained
separately; they are never called installed or fetched by the server.

The plan has no request or response hashes: those reviews do not yet exist.
The deployment proposal pins the plan. Each review sees both exact literals.
Changing source, assignments, policy, criticism, proposal or selected applications
requires a new plan/proposal and fresh applicable reviews.

Run the existing command:

    python -m orchestrator.prepare_deployment_bundle --root CHECKOUT --source EXACT_SOURCE --archive SOURCE_ARCHIVE --plan PREPARATION_INPUT --destination NEW_PRIVATE_PACKAGE

The package contains review-plan.json, review-files-a.json, review-files-b.json,
review-files-integration.json, proposal.json, and change-bindings.json. It
preserves selected original request/event/evidence bytes in change-inputs/.
Preparation makes no review claim.

## Keep the same saved context for every call

Use the existing courier from the exact clean checkout. For part A:

    python scripts/pilot_review.py --scope material-deployment-source-part-a --expected-source EXACT_SOURCE --file-manifest PACKAGE/review-files-a.json --private-dir NEW_PART_A --shared-context --change-store PACKAGE/change-inputs --change-bindings PACKAGE/change-bindings.json --private-evidence PACKAGE/proposal.json --private-evidence PACKAGE/review-plan.json --private-evidence PACKAGE/change-bindings.json --private-evidence EACH_COMMON_ORIGINAL --prepare-only

Repeat --private-evidence for every complete common original in the plan.
Use scope material-deployment-source-part-b, part B's manifest and a fresh
directory for the second call. Inspect each prepared request before its existing
single --run-prepared --request-sha256 EXACT_REQUEST_SHA invocation. Retain all
six originals and actual model/session metadata. A component scope is never
accepted by the public standalone deployment-review validator.

Keep PACKAGE/change-inputs unchanged through all three calls, including its path.
Record component outcomes separately. Do not regenerate final change context
from newer canonical heads. The gate compares actual reconstructed role-context
hashes, change projections and exact selected-application sidecars across all
three calls. Same source alone is insufficient.

The courier still caps each supplement at 2,000,000 bytes and a complete request
at 4,000,000 bytes. These byte limits do not guarantee token fit. Use available
capacity evidence and the existing bounded invocation. If the provider refuses,
preserve and reconcile the failure; do not retry automatically or trim required
source, literals or criticism to force a fit.

## Assemble originals and request the final judgment

After both actual source reviews approve:

    python -m orchestrator.prepare_deployment_bundle --assemble-components --bundle PACKAGE --part-a PART_A --part-b PART_B --destination NEW_COMPONENT_COPY

This validates both original protocols and assignments, copies their six files
without rewriting them, and emits component-receipts.json with their hashes.
It refuses an existing output and preserves incomplete/failed attempts. Created
directories are private regardless of the caller's umask. There are no provider,
host or change-record side effects.

Prepare the final courier with scope material-deployment, the integration
manifest, and identical context, saved change store and sidecar. Supply the exact
plan/proposal, every proposed and previous configuration literal, recovery,
all common criticism, component-receipts.json, and both complete original
component response.json files. The manifest binds every original request,
execution, protocol, intent and return. Full responses retain findings without
a driver paraphrase. Add all further relevant observations and criticism.
A planning allowance never authorizes omission.

Only the actual final integration session can supply applicable REVIEW events
for selected applications. Component approvals remain component evidence.
A negative/missing part, changed original, missing name, different context or
omitted final finding refuses the composed proof.

## Freeze and inspect the same evidence

Retain final originals at the normal bundle root. Copy review-plan.json,
component-receipts.json and component-reviews/a/ and component-reviews/b/ with
all six original files into the root-held bundle, alongside ordinary literals
and reviewed change chains. Preserve original change-inputs separately from
later reviewed changes. The ordinary installer and installed gate check the
composition before and after installation.

Local freeze preparation can use the same pure proof without bypassing protected
filesystem checks:

    final_review = deployment_review.review_originals(final_originals, source)
    proof = deployment_review.composed_review_bytes(
        proposal, proposal_raw, archive_files, final_review,
        plan_raw, component_originals, component_receipts_raw)

The caller first obtains exact bounded original bytes with its local reader.
This checks composition; ordinary target/readback and change-chain checks still
apply. The protected loader uses the same function after reading root-owned
originals. Stable component hashes travel through the existing immutable install
intent/receipt, preventing later substitution.

Humans and agents inspect the same manifests, assignments, full responses and
attributed changes. On refusal, preserve artifacts, identify the changed/missing
input, and prepare a new bound attempt under applicable authority. Pending review
never becomes approval automatically.
