# Roles and operator rotation

Current operator: **Codex, OpenAI family**. No rotation. Item6/synthesis accepted; Idea2 code and CPU adapter independently approved; the adapter is installed and its single execution is complete. Colab is unparked by explicit operator decision; author8 completed both corrections and synthetic tests; scientific review7 APPROVE and exact notebooks delivered. Opposite-family administrative capability remains uninstalled; current Claude route remains the reviewer. The operator owns infrastructure and sequencing; scientific code/conclusions remain with system author/reviewer.

| Work | Current author/operator route | Independent review route |
|---|---|---|
| Operator implementation | Codex / OpenAI | Existing Claude administrative implementation-review route |
| Scientific code and analysis | Existing system OpenAI author client and accounted scientific driver | Existing system Claude scientific reviewer |
| Future Claude operator implementation | Claude Code / Anthropic, after a clean handover | OpenAI through the existing author client used in a distinct administrative reviewer role; configuration support is pending review and installation |

**The operator's and scientific author's work must always be reviewed by the other model family.** Different sessions or model versions within one family do not supply that independence. Refuse a missing, unknown or same-family review assignment. Scientific author/reviewer routes stay unchanged during this rotation preparation. Administrative reviews remain administrative calls, even when they reuse the author client's transport; they may not be relabeled as scientific author calls.

The opposite-family administrative route must retain the existing independent verdict, exact source and approval bindings, tool-based review submission and qualification, usage accounting, uncertainty handling, isolation and limits. No new credentials are authorized. Merely changing a configuration label does not enable a route that has not passed tests and independent implementation review.

## Rotation trigger and procedure

Rotate at a completed milestone boundary or a weekly boundary, **never mid-task**. A weekly boundary means the next clean stopping point, not interruption of a live run. The first intended milestone is the execution plan, first reviewed Colab instructions, and the timing result. Partho has requested preparation, not an immediate role change.

1. Finish or explicitly park each bounded task. Reconcile existing model calls, provider jobs, tests, reviews and watchers against durable records. An open or uncertain attempt is not a clean handover point and must never be relaunched blindly.
2. Update [HANDOVER.md](HANDOVER.md), [CURRENT.md](CURRENT.md), the seven-line opening of [STATUS](outputs/STATUS.md), and the [13B execution plan](outputs/13B_EXECUTION_PLAN.md). Record actual versus reserved spending, original attempts, open decisions, exact commits/reviews and what must not be duplicated.
3. Run privacy, secret and infrastructure scans, then push approved safe work and status to `remote-server` and safe working branches. Verify remote hashes. Never merge to `main` or publish private evidence, patient rows, images, masks or caches.
4. The incoming operator reads the handover and operator decisions, checks the live state independently using existing read-only scripts, and confirms there is no other active operator. The outgoing operator records its final state and relinquishes ownership before the incoming operator makes a mutation.
5. Record the new operator family in the reviewed configuration and ROLES, select the opposite administrative review family, and run the focused route check. Refuse rotation if that route is unavailable or not installed. Preserve scientific routes and all history.
6. The incoming operator starts with a short plain-language update headed `Action needed from you`, then resumes the recorded next step. Ask Partho only about money or a Colab action; consult the opposite-family reviewer for other uncertainty under the standing rule.

## First swap gate (operator instruction)

Declare **Swap point reached** immediately after **Action needed from you** only when all six are true: execution plan written; first Colab instructions sent; timing diagnostic has a result; ROLES and HANDOVER current; opposite-family administrative review capability installed; and no model call or compute job running or awaiting reconciliation. Then finish the current step, update and push the handover, and wait. Do not start a successor task after the gate. The operator has not requested an earlier stop.

Current CPU milestone (12 October): Idea2 adapter5311301 independently approved in review71bf1a50,77tests and native read-only/writable controls pass. The single saved-output CPU execution completed and validated; no retry. Colab notebooks are delivered; Idea2 interpretation is accepted; no current server model or compute call is live. Human Colab folds 0 and 1 are active by operator report. The accepted interpretation retains the large-table inspection limitation.

Scientific reviewer-requested code corrections return to the scientific author through the normal revise loop, regardless of finding category. Administrative review applies to infrastructure changes; correction does not grant new data access, credentials, spending or execution.

Operator update12October: A1_repeat folds0/1 active on two unedited review7 A100 sessions; Drive mounted and estimate printed, but no completed epoch/output report yet. Next arms: multiwin, pnormct, pnorm_v2, L, then A1_repeat2. Compare Colab arms to Colab A1_repeat; repeat strengthens noise estimate before final conclusions. Decision is verbatim/hash-pinned privately9029bd20. Do not edit running notebook bytes.

Current next step: the multiwin author intake draft is ready privately with the new order and Colab-baseline rule. Prepare its normal scientific author/reviewer lane, then deliver exact approved files; provisional2-4activehours. Colab folds0/1 remain externally active by operator report. Timing, coverage-dependent arms, sandbox and rotation remain deferred; no swap point.
