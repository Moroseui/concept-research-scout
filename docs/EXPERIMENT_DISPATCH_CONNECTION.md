# Reviewed experiment package to fit dispatch

The experiment driver now enters the existing Modal executor through a separate
item-4 dispatch adapter. Scientific definitions and code remain author-owned.
It does not start a model, initialize another allowance or supply science code.

The immutable preparation selects an absolute `execution_provisioning` directory.
It must already be private and root-owned. After validated preprocessing, the
provisioner preserves a `READY.json` there, with schema
`experiment-fit-dispatch/v1`, exact release source and run, the SHA256 of the
actual reviewed package manifest bytes, and ordered jobs. Each job references a
root-owned runtime file by path and hash and the existing runtime binding.
The record remains fixed after the first dispatch tick. Provisioning itself is
a remaining connection; this module does not manufacture readiness.

The actual scientific execution plan supplies the ordered `fits` list. Each
entry declares `fit_id`, `stage`, `arm`, `fold`, `realization`, and `outputs`.
Runtime entries must match that list exactly. The author/reviewer owns these
choices and definitions. Runtime resource choices still pass the existing
provider checks and spending admission. Initial dispatch accepts segment one
only; checkpoint continuation remains a separate required connection and cannot
be represented as a fresh fit here.

One tick prepares a package, uploads the exact package, or calls the existing
executor's submit method. Later ticks observe running fits before another
launch. Submission uncertainty and partial upload are never retried implicitly.
Unknown or unavailable observations remain observations, not terminal evidence.
The executor retains the existing global/local ledgers, cost reservations,
provider checks, concurrency limit and duplicate protection.

No prepared runtime means a visible WAIT_EXECUTION_PREPARATION, with no provider
call. An execution marked COMPLETE only moves to COLLECT_EXPERIMENT; scientific
validation, interpretation, independent review and STATE/report updates are
still required. No legacy known-case route is used. Item-6 CPU execution,
preprocessing, health/resume integration and collection are not completed by
this connection.

Tests distinguish synthetic external services and root-provenance fixtures from
real internal connections. The integrated test passes the real scientific seal,
actual driver transition, package producer and provider-package verifier without
patching those functions. It found and fixed a missing private parent-directory
creation that mocked transition tests did not catch. No patient computation or
paid provider job is executed by these tests.
