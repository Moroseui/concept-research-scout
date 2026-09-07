# First handover implementation — current work record

Base: `7bba218e37b76a180d8ac35c34f2d30afe165143`, branch
`astra/infrastructure-milestone-record`. Prior hosted review and amendment remain
preserved; the readiness proposal is reviewed, not missing a review. No previously
successful run was repeated. SSH initially had no loaded identity; the operator
reloaded it and read-only access succeeded. Original five synthetic attempts and
five outcomes remained unchanged.

Current draft changes (not installed or approved for activation):

- Shared Actions/server admission uses the existing CAS ledger, separate server
  identities, common thresholds, duplicate binding and persistent midnight halt.
- Coordinator uses Store/SQLite and immutable stage receipts; a completed review
  survives disposition/bookkeeping failure. Missing receipts remain uncertain and
  cannot trigger blind retry. Independent eligible tasks progress past dependencies.
- Revision-bound pause/resume, read-only status and nightly identity dedup are
  implemented in the coordinator; production CLI/service wiring remains unfinished.
- Protected broker draft checks OS peer identity, exact destinations, approved source
  pins, operator-only reset with expected sequence/policy, and delegates to the
  existing publication and ledger primitives. Live grant remains inactive.
- Writer App credential adapter requests only the selected repository and explicit
  permissions, verifies returned scope, and removes temporary credentials from the
  environment on every exit. No App or credential was created or used.

Relevant synthetic tests currently pass. These are local implementation results,
not deployed acceptance. Remaining work includes the installed service/client
adapter, Actions provenance collection, persistent report/model handling and final
bookkeeping recovery, complete permission/ownership checks, hosted synthetic
verification and fresh Claude review. No permission packet is presented yet.

GitHub token-scoping implementation reference:
[GitHub App installation token API](https://docs.github.com/en/rest/apps/apps#create-an-installation-access-token-for-an-app).
The API supports explicit repository and permission restriction; a token or branch
name alone does not enforce our publication branch boundary.

Recovery wiring follow-up: a read-only broker status route verifies the original
console, prompt, answer and context hashes before returning a completed stage.
Absent evidence remains uncertain. Coordinator recovery records those originals
without invoking a model. Socket client disconnection no longer kills successful
bookkeeping. Report task identity excludes mutable review-queue status. Runtime
and broker integration remain drafts; no live activation is claimed.

The local Unix-socket regression needed sandbox permission for socketpair traffic
(`Operation not permitted`); it passed when run with that permission. SSH access
was restored by operator authentication. No model sign-in is currently requested.

Fresh source review at `306504d2664a848860f1aa45f2819ee29224236c` returned
REQUEST_CHANGES (actual reviewer `claude-fable-5`; author-operated, not merge desk).
The original findings and execution bindings are recorded in
`HANDOVER_RECOVERY_REVIEW_20260906.json`. Corrections enforce canonical role order,
isolate/cap final bookkeeping, distinguish pre-launch refusal from uncertainty,
and preserve control-write failures while processing subsequent valid requests.
A follow-up review is required; these corrections are not self-approved.

The selected 48/96 semantics passed a private synthetic ledger test: 48 warns,
96 admits and latches halt, 97 refuses, duplicate 96 does not recharge, and midnight
does not clear halt. No live ledger was initialized. Draft systemd units passed
`systemd-analyze verify` without installation or service activation.
The Actions artifact identity verifier is implemented and locally tested against
synthetic API metadata; actual protected API collection and workflow integration
remain unfinished. Socket unit contents now pass the same pre-publication text
scanner as other service units; forbidden case strings remain rejected.
