# Step(d): operator instruction, 2026-09-25

Step(c) approved at 5e4c02b8617d71a524f64c014877f3f3093a0ae0; original manual
review002 is APPROVE, preserved privately with its original scope.

The operator authorizes step(d) on a new laptop branch: Sprint10 is a known-case
system acceptance test, not new research. Build a manual executor using job_store
and accounting (submit package, status, collect), with no duplicate or uncertain
resubmissions. A one-transition driver uses only manual_context.build/prepare.
Sequence: spec author, opposing spec review, package, operator Colab run, collect
and validate, interpretation author/review, derived STATE update, short report.

At most eight stage invocations total: each of the four scientific roles may run
once plus one revision. No automatic retries or fallbacks. Maximum two review
rounds, fixed repair-plan blocker categories; unresolved blocker stops for the
operator. Record input sizes, outcomes, usage/provenance, elapsed time and human
interventions. Existing global controls are not reset by this bounded allowance.

No deployment, main merge, new paid resource, training, or access to the25 final
or24 reserve patients. Use existing subscription credentials only. Predeclare
comparison to original Sprint10 saved tables and numeric tolerance before run.
Stop for the operator to run the package, then stop with a final one-page report.

Original report SHA256: 41282f44b78094265aecb6c8580723b5b1cc97e579856d78903714e9bcc0bb90

## Operator clarification: engine review precedes all scientific calls

> Use my separate manual Claude session for the engine-code review, as in step (c). It does not count against the 8 calls; all 8 remain for the scientific stages.
>
> Order: finish and test the executor/driver diff, then prepare a review folder (branch, commit, diff, test logs, and how the driver enforces the call limit and uses only manual_context.build/prepare) and stop. After my review approves (max 2 rounds), you may start the driver's scientific calls. No model call before that.

Implementation state: prepared for manual engine review only. Scientific calls
remain held and unconsumed. CLI `init` requires an exact-source APPROVE report;
a scoped prior source approval cannot initialize this candidate.
