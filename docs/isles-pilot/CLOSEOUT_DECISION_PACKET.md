# PR #2 — bounded closeout decision packet

**Status: unmerged; new standing capability, N, state-writer permission and R1–R4
ratification remain pending.** The [operator-supplied Fable desk handoff](FABLE_DESK_HANDOFF_RECEIVED_20260906.md) reviewed
`1ecc3f9d5815fb1401bee48454dce197985d947f`. It does not approve the closeout delta.
The final exact head, main/candidate/tree pins and CI links are recorded in PR #2;
use those pins, not an older review checkpoint, for independent desk review.

## What changed since the desk handoff

- Controlled publication now checks commit metadata and every outgoing changed
  blob before transfer, including deleted intermediate files and merged side
  history. A reusable publisher accepts exact operation/inventory bindings beyond
  the pilot branch API; no additional production destination is authorized.
  Legacy `scout._push_checkpoint` can no longer directly push/rebase main.
- Artifacts and all owned Summary routes use pre-publication validation, including
  fixed infrastructure-failure messages and proposed limiter notifications.
- Shared CAS admission is implemented and tested. A separate admission job has no
  model credentials. Both jobs remain read-only; limiter config is PROPOSED/n=null.
  Activation and a protected writer/reset route need explicit permission decisions.
- Bootstrap authorship is recorded transparently; new commits identify Astra as
  an OpenAI agent. Operator sign-off is separate. No existing commit was rewritten.
- R1–R4 are appended as an explicitly unratified proposal, with the operator's
  corrections to publication enforcement, auth/cost, generation and branch order.

## Evidence to review

| Question | Evidence and conclusion |
|---|---|
| Publication coverage | [Route audit](PUBLICATION_COVERAGE_20260906.md). Current local credential has admin/push capability; direct Git/Contents/Git-data API writes can bypass scripts. Main is unprotected; results rules cover deletion/non-fast-forward only. Post-push CI is detection, not exposure prevention. No universal-protection claim. |
| Limiter number | [Measured dispatch record](DISPATCH_ACTIVITY_20260906.json): 48 recorded dispatches across 28 UTC dates, peak 12, proposed N=48 (4× peak), hard ceiling 96 admissions. N is not selected. |
| Limiter behavior | [Semantics/deployment boundary](DISPATCH_LIMITER.md), tests/test_dispatch_limiter.py: concurrent cross-branch admission, soft/hard thresholds, UTC rollover, midnight-latched halt, idempotent admission retry, counted reruns/replays, crash recovery, stale-writer conflict, explicit reset/init. Real Git transport exercised against a disposable bare repository; no public state was provisioned. |
| Authentication/cost | Existing Codex API-key arrangement and Claude subscription OAuth. A control-run-attempt count is neither a dollar limit nor a total Actions-job/minute limit. Provider allowances and experiment caps remain; no new credential/billing/provisioning authority. |
| 047 notebook | [Reproduction receipt](047_NOTEBOOK_REPRODUCTION_20260906.json): generator 469d29d, source pin 9216e6 and exact arguments/environment identified. Ten cell sources equal; top-level metadata equal; ten random IDs differ; byte identity false. No notebook cell ran. |
| 047 runner | [Authoring receipt](047_RUN_AUTHORING_PROVENANCE_20260906.json): original system probe_code and opposing probe_review receipts match parent commits and prompt hashes; recorded review APPROVE with no blockers. The direct staging-expression change 194cdcd matches subsequent reviewed bytes. package-colab did not generate run.py. |
| 2a-state | [Local/public reconciliation](BRANCH_AND_AUTHORSHIP_20260906.json): published tip and ten local reflog tips contained in main; known checkouts clean/no stashes at inspection. No separate merge/order decision required. |
| Scientific preservation | P001 executable d6a1184 and notebook 1a81c037, archive and existing reviews unchanged. The repaired scout.py means **current-tree patient execution needs fresh dependency review**. Verification certifies original approved bytes at frozen 1ecc3f9 and separately reports that block; it does not upgrade an approval. |
| Validation | Final full implementation suite: 310 tests / 20 subtests; state 47/47 and registries 4/4. Final exact-head isolated integration and hosted CI are reported in PR #2. Failed intermediate audit/test attempts remain recorded; original protocols/logs are private. Author-operated Fable reviews approved b5bc5c4 and the final runtime at 6ab1d3d; these are not independent desk approvals. |

## Remaining human-functionality exceptions

Campaign Actions discussion/brief/proposal/specification/code/repair/curation are
supported; the prior real confer demonstration and zero-call replay remain valid
at their recorded executable pin. This batch does not claim full legacy parity:
global/nightly scouting, arbitrary numbered-idea Q&A, whole-corpus librarian
mutation and automatic improvement PRs remain exceptions. Private result return
and import are not public Actions uploads; interpretation is gated and does not
ratify science. Legacy CI checkpoint publishing now requires an explicit reviewed
binding and otherwise refuses. [Complete inventory](HUMAN_CONTROLS.md).

## Decisions requested together, with reserved decisions separate

1. Obtain independent desk review of the final PR head and actual main candidate
   (full main→head diff plus incremental 1ecc3f9→head diff). Internal Fable reviews
   in this branch are author-operated evidence, not substitutes for that desk.
2. Ratify, amend or decline the [corrected R1–R4 proposal](CLOSEOUT_RULINGS_PROPOSED.md),
   including a chosen N (recommendation 48). No value or standing grant is inferred
   from silence, tests or merging the implementation.
3. Choose whether to leave the limiter inactive/read-only or approve a narrowly
   isolated state-writer/reset permission design using existing credentials. A
   repository-wide write token is not ref-scoped. Stronger all-public-branch
   enforcement requires an exclusive publisher/remove-bypass design; that change
   is not authorized or implemented by this closeout.
4. After desk review and explicit operator sign-off, decide on a **normal merge**,
   preserving commit identities and the pilot branch. Repeat integration if main
   moves. Keep the PR unmerged until that decision.

047 scientific landing/acceptance, the separately rehearsed public-history cleanup
and P001 launch are **not included** in any infrastructure merge. No queued 047
landing proceeds automatically. Missing original successful console and exclusion/
disposition gates remain; no evidence or ratification has been manufactured.

## Accepted review limits

Evidence size limits can block a model-reviewed proposal; original audit prompts
are not silently removed to fit. Reusing a BLOCKED request identity replays that
block; repair then deliberately change request ID. Artifact redirects strip
GitHub authorization; the ordinary GitHub JSON API helper still assumes its API
endpoints will not redirect cross-host. Source SHA is a confirmation of the
selected branch revision, not an alternate checkout selector. Committed review
hash records are not cryptographic operator signatures. These residuals are
visible to the final desk; no broader safety or quota guarantee is asserted.
