# Failed fit cleanup in the experiment executor

A positively observed FAILED item4 result, including a failed input guard, now
enters the existing executor's failure cleanup. It preserves the observation
with its exact job, provider and binding identity before any stop request.
The existing full reservation remains counted as UNCERTAIN and the job is
blocked. It is never marked COLLECTED or scientifically complete.

One immutable termination intent precedes the provider stop. A verified stop
receipt is preserved separately. Later status, submit and collection requests
return the saved failure without relaunch, collection, refund or another stop.
An interrupted/uncertain stop request remains reconciliation-only. RUNNING,
UNKNOWN and observation timeouts cannot trigger this failure path. The fit
health monitor and this transition share the existing executor lock. M3's
original failure behavior is unchanged.

The full loop still needs its reviewed execution-package adapter, preprocessing
and fit dispatch, collection validation, scientific interpretation and final
report connection. This cleanup connection is necessary but is not evidence of
an executed experiment. Tests use synthetic data and provider endpoints; the
actual provider methods, input-proof verifier, job store and accounting run.
