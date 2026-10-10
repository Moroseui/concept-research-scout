# Operator handover

**Current owner: Codex / OpenAI. Rotation is being prepared, not performed.** Updated 10 October 2026. Read [ROLES](ROLES.md) for responsibilities and the independent-review rule. This file is updated in place at every stop; it is a factual handover, not an approval or a scientific verdict.

## Goal and operating direction

Use the system to understand infarct prediction from admission CT, while making it easier and more robust for humans. Keep analysis and ideas, 13B execution, private meeting support and system usability moving in parallel. Ideas need a biological, mathematical or computer-science basis, a testable prediction and attribution of gains to placement versus amount, size, region and fragmentation. Dissect unexplained gains. Scientific code and conclusions belong to the system author and reviewer; operator work is infrastructure and coordination.

Prefer the shortest safe path and batch reviews. Use existing access only. Never access the 25 locked or 24 reserve patients, create/change credentials, publish private patient-derived material, merge to main, or edit BACKLOG. Public aggregate backup remains limited to the explicitly authorized, scanned outputs. Ask the operator for money or a required Colab action only; use Claude for current engineering uncertainty. Do not relax a refusal to get past a block.

## Workstreams and next steps

| Workstream | Current evidence/state | Next real result, reason and estimate |
|---|---|---|
| Analysis and ideas | Item 6 is complete and independently approved; all 352 comparable Sprint 14 values reproduced. New intake includes item 6, three benchmarks, two smokes, Sprint 13A/14, the preserved size-specialist idea and prior reviewed directions. The complete parked-ideas document has not been located. No new synthesis call admitted yet. | Author's actual synthesis, ranked hypotheses and case-selection proposal, then scientific critique. Target 1-2 h after reviewed admission. This extracts understanding from results already available. |
| 13B / Colab | [Execution plan](outputs/13B_EXECUTION_PLAN.md) assigns all 8 arms x 5 folds explicitly to Partho on Colab. Original notebook has stale defaults and a smaller smoke cohort; it is not the new handoff. | Scientific author prepares a matched 99-development/fold 0 baseline smoke notebook; reviewer judges it; operator packages exact settings and private return instructions. Target 2-4 h from October 10 resumption. Colab must not wait for the timing diagnostic. |
| 13B / timing | A100/H100/B200 first epochs included warm-up. Two B200 smokes have candidate 71-90 s epochs without an established plateau. CPU-starvation A/B has not run. Timing author 24 is activated but unstarted. | Reviewed/native-validated B200 diagnostic, 15 epochs each,16 CPU versus 32 CPU and corresponding workers, telemetry/checkpoint timing, hard stops/no automatic GPU retry. Conditional 2-3 h after author/native/scientific gates; re-estimate after the author result. |
| Professor meeting | Private production workflow prepared. No actual cases selected or images read for this task. | Scientifically reviewed selection rule frozen before viewing images, then private panels of admission CT, follow-up MRI, reference/model masks and permitted clinical information. Selection proposal alongside first synthesis; panel ETA after private source inventory. |
| System usability | Dated-cap patch has 45 focused tests and a passing real-driver rehearsal on copied ledgers with a stubbed backend. Analysis/Colab sibling preparation and bounded synthetic author feedback are held engineering candidates. | Independent implementation approval and installed admission; then same-call synthetic feedback after actual isolation checks. Keep these limited to removing concrete barriers. |
| Operator rotation | ROLES and this handover drafted. Opposite-family configurable administrative review is not implemented/installed yet. | Reviewed OpenAI administrative-review route before a Claude operator takes over. Prepare alongside current work; rotate only at the agreed clean milestone or weekly boundary. |

## Limits, spending and decisions

Item 4: stage 1 $150; timing diagnostic $25 inside stage 1; full-training projection gate $1,200; total $1,275. Full training requires scientific smoke acceptance. Coverage-dependent zscore/histeq arms remain held for unverified source coverage. Identified provider compute actual $24.39800404; stage 1 actual-plus-open-reservations $114.397673; diagnostic commitment $4.286495. These are different quantities; model charges are separate. Reconcile closed provider attempts to actual billing and release only confirmed excess, retaining both original and actual figures. Never release open/uncertain reservations.

October 10UTC only: operator authorized 100 model calls, returning to 50 afterward. Source passed independent review; the held installation failed service-account verification because five new directories lack intended group traversal. A narrow reviewed directory-only repair is being prepared; do not reinstall. Latest usage 51: 9 scientific author, 5 scientific reviewer, 29 administrative review, 8 direction. All prior usage remains. Proposed parallel preparation allowances are process changes for Claude to judge, not installed caps: two 8-call lanes alongside existing item 4 scope, actual shared accounting preserved. No money decision is pending.

## What is running or must not be duplicated

At 20:56 UTC, administrative review call 51 was COMPLETE and its unit inactive with PID 0; no scientific call or GPU experiment was running. Its genuine APPROVE report is c7b151f22001f60fff51520c350a6e39ee127ea9e76f0f0574037867a70cf20a for source b2daefc0a6f2eae6b31a62901a974efbb20e6bd6. The review cost $4.0183349999999995, separately from compute. Installation then failed actual service-account verification: five new directories retained restrictive modes after creation under umask 0077. Files, source approval and original failure records remain preserved. Do not rerun the consumed installer or call 51. The component is held and not operational; its completion receipt alone does not establish successful verification. The narrow repair and B/Colab preparation are being batched for normal independent review.

Author 24's earlier activation is consumed; do not repeat it, start old author 23 or reuse old grants. No new author invocation has started. Existing cleanup/retention timers remain enabled; they are housekeeping, not scientific jobs. Reconcile exact live handles before any successor.

Engineering workspaces and prior failed/rejected attempts remain private and immutable. The abandoned SPEC-only recovery must not be installed. Author23 remains unaccepted; author22's original uncertain ledger row remains preserved with separately qualified terminal proof. Never treat a receipt copied into a new context as a fresh grant.

## Resume safely

1. Read the latest seven-line STATUS, this file, execution plan, canonical private operator-decisions record and private CURRENT. The private recovery directory is adjacent to the project checkouts under `isles-pilot-private-evidence/recovery-20260910/autonomy-batch-20260927`. It contains the actual operation scripts and exact-source evidence; it is never pushed. Do not infer a launch from a narrative status file.
2. Check the UTC clock, active operator ownership, existing service/PID states, provider job handles, test/review outcomes, and read-only ledger counts as the established service account. Root must not open live SQLite directly. An intent without a qualified terminal result means reconcile, not retry.
3. Current dated-cap candidate: private `temporary-daily-cap-20261010`, source b2daefc0a6f2eae6b31a62901a974efbb20e6bd6. Read its HANDOFF, preserved installation failure and pending repair operations. The original source is approved, but installation is held after failed verification. Do not rerun it. After a separately approved repair and successful service-account verification, its new host wrapper owns start/pulse/stop for the new unit; old author 24start scripts target the old 50-call route and must not be used for it.
4. New analysis/Colab candidates are in `workstream-b-aggregate-20261010` and their exact prepared plans; sandbox candidate is `author-synthetic-sandbox-20261010`. None is installed. Preserve ordinary admission, global single-model-call/uncertainty refusal, scientific stage gates and all old row identities. Validate both sibling and existing item 4 connections on copied history before launch.
5. Obtain the first scientific synthesis/review and the named reviewed Colab notebook. Send Partho explicit notebook/settings/return instructions only once that artifact exists. Keep the execution plan current and report next results/estimates per workstream.
6. At each stop update this file, CURRENT and STATUS; scan and push safe changes to remote-server and safe astra branches; verify the remote hashes. Never push raw private ancestry or evidence. Latest verified backup before this rotation draft is bc2bf6a2a15f443df1c30ee5f92e4fe4317f502a; main remains c17281a11dd2ed15e59cc38bbb526fb6c466b145.

## Access names only

Use existing server SSH access, the existing research service account, the existing OpenAI author-client login, the existing Claude reviewer login, existing Modal account, existing Google Drive access to isles-pilot, and existing GitHub backup login. No credential contents, credential files, key names or connection endpoints belong here. If access is unavailable, reconcile the existing mechanism; do not create or rotate credentials. Partho may need to unlock existing access privately, never supply secrets in chat.

## First swap gate (operator instruction)

Declare **Swap point reached** immediately after **Action needed from you** only when all six are true: execution plan written; first Colab instructions sent; timing diagnostic has a result; ROLES and HANDOVER current; opposite-family administrative review capability installed; and no model call or compute job running or awaiting reconciliation. Then finish the current step, update and push the handover, and wait. Do not start a successor task after the gate. The operator has not requested an earlier stop.

Current gate: plan complete; Colab instructions not sent; timing result absent; role/handover drafts current but review pending; configurable OpenAI administrative route not installed. No swap declared. Reconcile live calls/jobs again at the eventual boundary.
