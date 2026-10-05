# M0 implementation-review route

Status: candidate, not installed or accepted live. No dependency on the archived implementation-review automation, controller or H2.

## Small supported path

`autonomy_review.prepare` captures explicitly named source blobs from an exact Git commit, original scoped evidence and runtime bytes. The packet manifest hashes every supplied file; `prompt.txt` is generated from a fixed template. All evidence remains file-readable; it is not embedded into the starting prompt. The caller must make all affected connections accessible; the manifest states the exact selected scope, not coverage of omitted files.

The native runner reuses RC6's `manual_auth`, `manual_isolation`, host proof and whole-package checks. Claude is in plan mode, with only Read/Glob/Grep and an empty strict MCP configuration; Bash, edits, writes and delegation are denied. The packet is a separate read-only bind. Native logs use the isolated per-call home/workspace. Only the separate implementation-review credential is present; executor/GitHub/Modal credentials and host private data are absent.

The root preflight binds an explicitly allowed packet, installed file inventory and reviewer runtime. It calls RC6's unchanged AppArmor/needrestart policy check. It does not alter the selected scientific release, read a lane database as root, control upgrades or touch any old unit. The new unit name must start `research-manual-sprint10-` so the existing needrestart exclusion applies. The existing `/run/research-manual-sprint10/host-check.json` belongs to the new RC6 family, not the held old routes. Its invocation-bound proof refuses concurrent stale/overwritten observations.

## Calls and original outcomes

A `job_store.Store` database records reservations and completions in one transaction per change. `autonomy_calls` records one charged unit per actual reserved native invocation, date, round, source/runtime/packet/preflight bindings and native usage. No reset/refund/retry API exists. Two rounds per change; round two requires the genuine prior rejection and changed source, configuration or substantive evidence (a new brief alone is insufficient). Repeated run/status does not launch again. Missing completion is RUNNING/uncertain and requires inspection of its actual unit/process handle, never inferred retry. A 20/day ceiling is conservative for this reviewer; M2 must integrate scientific admissions into this same daily ledger before claiming the batch-wide cap.

No scientific call is authorized by a source review. M0's two implementation acceptance invocations are outside the 30-call M2?M6 scientific acceptance allowance. Existing completed six-call Sprint10 records are never modified.

Claude's final result must exactly match the final native assistant text. Qualification requires one genuine native session, observed model, usage, successful scope/source reads, the exact source/runtime/packet bindings, an explicit supported verdict, and no forbidden tool. Read receipts establish the recorded reads, not inspection of every packet file. Missing evidence or an invalid report remains a failed charged result; a genuine rejection remains a rejection.

The receiver writes the final text verbatim once and seals its hash beside the original stream. The unit's root finalizer makes the invocation folder root-owned/read-only. Its parent must be root:partho mode 1770, preventing the unprivileged driver from replacing root-sealed folders. Reconciliation revalidates report, original stream and bindings. No report-edit/import-replacement command is provided. Root remains trusted recovery authority and could deliberately undo filesystem protection; this is not a claim of tamper resistance against a root administrator.

## Server entry point (prepared, not installed)

`deploy/autonomy-review/review@.service.in` uses partho, NoNewPrivileges, ProtectSystem=strict, PrivateTmp, no restart, and a 1100-second supervisor around the bounded 900-second native invocation. Both root hooks use `python3 -s -B`. Credentials remain in the operator-created dedicated login; each call copy is deleted in `finally`. Existing code/tool packages are reused, not installed again.

The M0-only tools/deploy_autonomy_review.py now prepares a separately verified versioned installation. It must establish a root-owned versioned source copy, a bound request allowlist/runtime and root-owned sticky state parent, render and verify the separate service template, and exercise its credential-free native/denial checks. This is M0 bootstrap work, not promotion of the scientific lane. No acceptance launch is permitted before those checks and the dedicated login pass.

## Acceptance fixtures and remaining gates

Private fixtures are at `../m0-acceptance/` relative to the checkout. RC6 and candidate-b each have a 1,804-character/byte initial prompt and 57 files. All originals are preserved. The expected-outcome oracle is outside both packets. Candidate-b is a separate scratch Git repository; its deliberate omission of the whole-package check is never installed. Live acceptance requires RC6 APPROVE and candidate-b CHANGES REQUIRED. Synthetic tests cannot supply either verdict.

Before M0 completion: complete service wiring and live read-only/tool denial verification; obtain the dedicated operator login; launch each fixed request once; preserve/reconcile both genuine outcomes and charges; verify repeat status causes neither call nor charge. If either review is incomplete or produces an unexpected outcome, preserve and diagnose it under the batch stop rules. Do not manufacture the required result or relaunch equivalent material.


## First live outcome and bounded completion (2026-09-28)

The first RC6 acceptance invocation ended definitively with native `error_max_turns`, counter30, exit0, no report, and one preserved charged invocation. Its source scope and originals are unchanged. Pinned Claude2.0.37 increments that counter on user/tool-result messages (starts at1), not on final answers;44 assistant messages and30 tool calls were recorded. It ended after209.487 seconds, below the900-second bound. `../m0-bootstrap/NATIVE_TURN_COUNTER.json` binds the exact client source excerpt; the native stream remains authoritative.

M0 bootstrap now allows60 read turns per invocation; invocation count,20/day, two rounds, timeout, isolation and final approval checks are unchanged. Only the exact known first-round30-turn terminal failure can enter round2 as an explicitly linked completion. The source packet and genuine native inspection are retained, with originals retrievable and no prior verdict invented. The existing queue must match its FAILED receipt and native hash; uncertainty, other errors, changed hashes, a final report, a60-turn exhaustion or any third round refuse. This is use of the batch's second round, not a reset, refund or general retry facility. If the completion does not qualify, stop for the operator; do not relaunch it.

The installer permits a new immutable reviewer version only with the previous root-owned installation receipt/hash, unchanged previous installed files, no active previous invocation and the SAME root-owned sticky state directory. It does not clear or migrate the ledger. Old versions, the failed outcome and charge remain. This is still initial M0 bootstrap, not a change to the scientific selected release or archived controller.
