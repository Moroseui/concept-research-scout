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
