# Roles and operator rotation

Current operator: **Codex, OpenAI family**. No rotation has occurred. The operator owns infrastructure, venues, sequencing, accounting, status and handover; it does not author scientific code or substitute its conclusions for scientific review.

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
