# One linked interpretation recovery, separate from credentials

Operator decision is preserved verbatim in STEP_D_LINKED_RECOVERY_DECISION.txt.
Only run sprint10-stepd-a9123b81e3ef32ee, original failed author invocation1 and its
exact unchanged row/receipt are eligible. Failure remains UNCERTAIN with its
original charge. No scientific output or table is recomputed or relabeled.

Credential diagnosis is private metadata-only evidence in the review folder.
No lost copy-back or expiry at failure is demonstrated. Existing wrapper, refresh
handling, native clients, read isolation and input assembly are unchanged. The
operator performs any login; no credentials are changed by this preparation.

The old driver has no supported recovery route. The minimum added connection:
manual_recovery.apply (exact decision + source APPROVE + failed-row binding)
-> immutable application plan -> runtime configuration + transactional recovery
permit/state transition -> existing driver/model_step -> existing reservation.
No model is invoked by applying the plan. This extension is an engine change,
not a claimed credential fix, and needs focused independent approval before use.

- Application preserves original lane configuration/state in the plan, all calls,
  prior approval, accounting and decision request. Reapplication cannot reset
  progressed state. A crash after writing configuration leaves BLOCKED/no permit;
  reapplying the same plan completes the transaction, without a model call.
- Runtime configuration separately binds the independently reviewed successor;
  original scientific source3a2d5c3 and original source approval stay intact.
  Subsequent receipts include both original failed-call link and recovery runtime
  source. Engine/data/context guards and publication boundaries stay in effect.
- Only this original UNCERTAIN row is excepted from later admissions. Any further
  failed/uncertain invocation blocks. Nothing erases/refunds the original.
- This run's interpretation-author limit is3; ordinary roles remain2 and total
  calls remain8. Invocation2 is the single recovery; invocation3 can be reached
  by the driver only after the first opposing review requests revision. Reviewer
  rounds stay2. No additional recovery or retry is created.
- Recovery workspace numbers use recorded invocations, so original workspace1
  is preserved and the new call uses2, with a possible reviewed revision using3.
- Accounting/halt engine, science, scanner, collection, validation and Colab
  code are unchanged. apply refuses a HALT. Native launch checks remain intact.

One existing synthetic full-lane fixture excludes already-generated acceptance
artifacts when copying its fresh-lane inputs. The real spec/review now exist at
baseb852c55; blindly copying them caused an immutable-artifact conflict in the
synthetic run. This adjusts only fixture setup, not a production gate.

Focused review: exact exception scope, immutable failure/accounting, exact-source
approval and runtime binding, idempotence/partial recovery, workspace numbering,
third-author and eight-total caps, and ordinary-path regressions. Tests are
synthetic except the unchanged isolation tests. No model or live lane mutation.
The stale decision-request evidence pointer stays in the later small-fix batch.
