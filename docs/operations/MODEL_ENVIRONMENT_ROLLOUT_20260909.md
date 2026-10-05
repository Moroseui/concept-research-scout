# Reviewed main controls and model environment: implementation candidate

Status: **local candidate, not deployed or activated**. The operator already
approved the restriction design through
[PROTECTED_HANDOVER_APPROVED_20260908.json](PROTECTED_HANDOVER_APPROVED_20260908.json).
[Main protection was installed and read back](MAIN_PROTECTION_INSTALLED_20260908.json):
pull requests and the existing `basic` check are required, force pushes/deletion
are refused, and the writer App has no bypass. Preserve that completed work.
An independent review and exact operator main-merge decision remain separate.

This candidate changes only the generated main-control wiring and its focused
tests. The seven phone controls retain their inputs, shared system stages, model
roles, source review, checked artifacts and no-patient-execution contract. Their
callers no longer forward repository model secrets. The reusable `run` job waits
for credential-free admission, requires the intended repository's main-branch
manual dispatch context, and names the dedicated `research-models` environment.
The admission job receives no environment or model secrets and gives a direct
message when invoked outside that context. Existing full-input
`actions_runner.reviewed()` checks still precede authentication/model steps.
The old review receipt is preserved; it cannot approve this changed source.

GitHub environment secrets belong to the job inside a reusable workflow;
`workflow_call` is not a route for passing an environment's secrets. Therefore
the called `run` job declares the environment and reads its two existing secret
names there, without a caller `secrets` mapping. This follows GitHub's
[reusable-workflow secret semantics](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).

## Exact rollout prerequisites

1. Record immutable candidate/base commits, complete generated-workflow diff,
   focused verification and a fresh genuine `human-controls` review covering all
   `orchestrator.actions_runner.REVIEW_FILES`. Update the actual review records
   through the existing review route, never fabricated approval. Independent
   main integration review must examine the final complete outgoing history,
   scientific/publication boundaries and effective merged tree, not only this
   small environment patch. Resolve any existing main-integration dependencies.
   Then request the operator's exact main merge decision. This candidate does not
   authorize a main merge or publication through the writer App, which lacks
   Workflows permission.
2. Reuse the existing privately preserved model credentials. Configure exactly
   `research-models` in `Moroseui/concept-research-scout` with selected deployment
   branches/tags and exactly one **branch** rule named `main`; add no tag rule.
   Record/read back repository ID, environment ID, policy and secret **names**.
   Keep `OPENAI_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN` only in that environment after
   the staged canary succeeds. Preserve original private credential storage and
   the distinct Codex API/Claude subscription arrangements throughout.
3. Verify actual environment policy before any secret-consuming canary. YAML can
   reference an environment but cannot configure branch protection; referencing
   a missing environment can create it with no configured protection. Use GitHub's
   [environment management controls](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
   and retain the readback. No environment, secret, dispatch or rule change was
   performed by this implementation task.

## Bounded canaries, no models or patient work

After the separately approved merge and environment setup, dispatch the existing
`results-validate` control on `main` with mode `status`, a unique recorded request
ID, and the exact merged source SHA. It uses deterministic existing result
readiness and never enters `campaign_pipeline.execute`. Save the Actions
run/attempt/source identity, job/step outcomes and checked result artifact. The
`Existing hosted authentication` step must itself succeed: its existing
`continue-on-error` setting means overall workflow success alone does **not** prove
credentials were available. Accept only the appropriate deterministic `READY` or
`WAITING_FOR_RESULT` status, with no scientific dispatch or generated model stage.
This canary verifies credential availability/auth setup, not model inference.

Before removing the repository-level copies, verify environment secret names and
policy, the successful main canary, and continued access to privately preserved
originals. Then remove only the two repository-level model-secret copies through
the approved restriction route and record the resulting names-only inventory.
Repeat the same bounded status control once with a fresh request ID to establish
that the deployed main job still obtains its environment credentials. Do not
infer origin from a positive canary while repository copies still exist.

For the negative path, a nonmain manual invocation of these updated controls
must fail in credential-free admission and never start the model job. If actual
environment-policy denial still needs separate proof, prepare a temporary,
reviewed canary workflow on an unprotected branch: a single job referencing
`research-models`, with no checkout, model command, secret reference or write
permission, and only a fixed synthetic success marker if admitted. Its job must
be refused by the selected-main environment policy. Record the exact branch,
workflow SHA and observed GitHub refusal; a skipped job caused only by a YAML
`if` is not proof of environment enforcement. The temporary workflow is a
separately reviewed publication/dispatch operation, not created or run here.

Each canary is one bounded invocation, without retry loops or live-limit
exhaustion. Failures preserve receipts and stop the affected rollout step.
Existing admission remains in its recorded inactive state; this packet neither
initializes a ledger nor activates the limiter, unattended turns or scientific
execution. Refresh the protected collector's reviewed caller/reusable-source
allowlist only to the independently reviewed final merged identities before any
later shared-admission activation.

## Remaining limits and handover evidence

Environment policy restricts branches, not an arbitrary list of workflow paths.
Exact reviewed main code and source-bound admission supply the workflow identity
checks; future main workflow changes require the same review/merge discipline.
Repository-level copies and any organization credential grant to this repository
must be reconciled before claiming a model-secret restriction. Owner and
administrator privileges remain outside the application-level boundary. GitHub
describes when jobs receive secrets and the available branch policy options in
[deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

The final finite merge/rollout packet needs: reviewed candidate plus effective
merge tree and base/head pins; fresh full-input adapter review; `basic` CI and
focused test receipts; preserved current main protection readback; configured
environment/branch-policy readback; names-only credential relocation inventory;
the positive and negative bounded canary receipts; protected collector source
allowlist reconciliation; and the still separate unattended activation decision.
Code completion or a successful status canary is not laptop-independent operation.
