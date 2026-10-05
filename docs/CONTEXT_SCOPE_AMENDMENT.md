# Step(c) operator scope and artifact selection amendment

Recorded from the operator's current instruction. This narrows the implementation task; it is not scientific execution or deployment authority. The exact v2 plan remains in REPAIR_PLAN.md. CONTEXT_PRIVACY_AMENDMENT.md remains applicable. No model calls of any kind; the operator will launch the separate manual review.

> Yes: each stage receives an explicit, relevant selection of current artifacts, with two conditions and a scope narrowing.
>
> 1. Selection map. Implement an explicit per-stage map in code (stage -> artifact types it receives), listed in the report. Anything not selected stays readable by path for operators.
>
> 2. Unresolved criticism as records, not transcripts. Extract each unresolved finding into the register as its own record (id, source path + span, the finding's text verbatim, severity, status). Stages receive all applicable open finding records; full review transcripts and "unreviewed tails" are not carried into inputs. A finding closes only with a cited resolution. This is lossless for the binding content and is the intended size fix.
>
> 3. Narrow the scope. Finish step (c) only for the assembly routes that step (d) will use (run spec author/review, result interpretation author/review, and whatever the manual executor lane needs). List the other route families as legacy: not used by the driver, not covered in this step. Do not work through all 24.
>
> 4. In the report, list each of the 51 test-fixture changes with a one-line justification, and confirm no production gate changed.
>
> When the step (d) routes fit under 200,000 characters on real data with the obligation, stop and closed-obligation tests passing, stop and prepare the review folder. Do not wait on the other routes.
