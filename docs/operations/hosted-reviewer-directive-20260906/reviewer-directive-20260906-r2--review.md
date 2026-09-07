# Fresh internal review — reviewer directive v2, deployment closeout evidence and readiness implementation

**Reviewer identity:** Claude Fable 5 (`claude-fable-5`), fresh reviewer session, no execution-worker context. **Directive:** CLAUDE_REVIEWER_DIRECTIVE.md `13b94fc1…`. **Canonical direction:** `5cc0a9f1…` — note this supersedes the `c643bc41…` version bound into the orientation cycle; prior findings were made against the older bytes. **Reviewed source:** commit `a0d56c79…`; task packet `a3be3e82…`; collector `3aca3103…`. **Supplied:** ten canonical documents, proposal packet (non-authority), task state, ten typed evidence responses, previous findings. **Unavailable:** the three named onboarding/deployment originals; any v2-review execution receipt; any live execution observation.

This is internal cross-family review only. It grants no ratification, launch, merge, activation, or credential authority; all reserved gates stay exactly as recorded.

## Overall assessment

The evidence broker, hosted-context builder, and readiness packet are honest and well-bounded. No supplied artifact overclaims: every historical record is labeled `HISTORICAL_DOCUMENT_NOT_CURRENT_EXECUTION_PROOF`, every live observation carries `execution_proven: false`, and the readiness packet's fallback deliverable is a gap list, not an invented result. Scientific direction remains aligned with the admission-imaging prediction goal; desk work (charter proposal, source-check amendment, readiness v2) is real progress and setup is not displacing it. The main gap is that **no current execution proof exists for any deployed claim**, and the readiness v2 packet itself lacks an opposing review record.

## Findings

**F1 — No current execution proof for deployment-closeout claims.** Blocker (affects `deployment-closeout` only). Evidence: all ten collector responses return historical documents; the only current observations are unit configuration (`CURRENT_CONFIGURATION_ONLY`). **Verified** as configuration: `research-system-controller.service` is loaded, hardened (`User=research-controller`, `NoNewPrivileges=yes`, `ProtectSystem=strict`, MemoryMax 512 MiB) with an active timer — but inactive, never observed running. **Untested:** laptop independence, restart recovery, provider backup, recurring nightly loop. Consequence: no closeout, unattended-operation, or 24–48-hour independence claim is supportable. Smallest action: a scoped collection task capturing one supervised controller-triggered cycle's live properties and completion receipt — not an inferred pass. Unrelated desk science continues.

**F2 — Readiness v2 packet has no opposing review record.** Blocker (affects the Wednesday "reviewed readiness packet" deliverable, not the packet's content). Evidence: `p001-readiness-20260906-v2/round-1/readiness.md` is supplied without a `review.json`; the round-1 APPROVE belongs to the earlier charter packet. **Verified** absence in supplied evidence. Consequence: the Wednesday target is a *reviewed* packet; this one is authored but unreviewed. Smallest action: run the existing opposing-family review round on the v2 bytes and record its receipt.

**F3 — This v2 review's own execution receipt.** Suggestion. The closeout checklist states deployed v2 review is pending its receipt; this session is that review. **Untested** whether the adapter records it. Consequence: without the receipt, the closeout row stays honestly open. Smallest action: adapter attaches this review with its bound context hashes per REPORTING.md.

**F4 — Collector mislabels absent units.** Suggestion (affects `reviewer_evidence`). Evidence: `research-system-orientation-20260906.service` returned `LoadState=not-found` yet status `CURRENT_CONFIGURATION_ONLY` with default properties; the test fixture does the same. **Verified** from code and packet. Consequence: a reader could mistake systemd defaults for configuration. Smallest action: emit `UNIT_NOT_FOUND` when `LoadState=not-found` (and a degraded status on non-zero returncode).

**F5 — Coarse evidence-kind mapping.** Suggestion. `installed_sources`, `resource_limits`, `restart_recovery`, `backup_recovery`, and `laptop_independence` all resolve to one of two checklist documents; `installed_sources` returns no actual source-pin inventory. **Verified** from `SOURCES`. Consequence: typed requests cannot obtain kind-specific evidence even where it exists. Smallest action: map each kind to its dedicated receipt where one exists, else return `UNAVAILABLE` explicitly.

**F6 — Envelope trust boundaries undocumented.** Suggestion. `hosted_context.envelope` accepts `verified_source` from the caller without checking it against the tree, and only `FileNotFoundError` is handled in `collect` (other `checked()` failures crash rather than report). **Verified** from code; fail-closed, so low risk. Smallest action: document caller responsibility for the commit binding; wrap other read failures as an explicit refused-record status.

**F7 — Tmax voxel-unit provenance.** Carried forward, open (affects `50-p001-launch`, already gated). The source-check amendment correctly leaves units unresolved; the readiness packet correctly treats this as an evidence gate, not a repair. Smallest action unchanged: claim-specific primary documentation check in permitted desk work.

## Prior findings — dispositions

- *Sandbox/resource properties unestablished:* **partially resolved** — live controller configuration is now observed (F1); executed-UID/runtime evidence for actual cycles remains open.
- *Report generator gaps (durations "unavailable" despite intervals; open inbox reasons unsurfaced):* **carried forward open** — no evidence of repair supplied.
- *Reconciliation/checked-source coupling documentation:* carried forward.
- *Authentication resolved; do not re-request sign-in:* **remains resolved**; no new evidence justifies reopening.
- Human-usability: documented start/progress/steering/recovery routes and repeat-request dedup are real (HUMAN_CONTROLS.md); only `confer` was exercised with real models, and deployed steering/interruption/takeover acceptance remains honestly **untested**.

## Typed evidence requests

```json
{"kind":"service_runtime","purpose":"Properties of research-system-controller.service captured while ActiveState=active during a supervised run, to establish executed User and sandbox settings","affected_task":"deployment-closeout"}
{"kind":"completion_continuation","purpose":"Execution receipt for this v2 review cycle and any controller-triggered cycle after 2026-09-06T22:43Z","affected_task":"deployment-closeout"}
{"kind":"reporting","purpose":"Whether nightly reports now include per-job durations and open decision-inbox reasons (prior finding)","affected_task":"reporting"}
{"kind":"backup_recovery","purpose":"Operator-confirmed provider backup and account two-factor evidence, or explicit UNAVAILABLE","affected_task":"provider-recovery"}
```

**Disposition recommendation:** accept the collector and context builder as implemented with F4–F6 as follow-ups; obtain the F2 opposing review before presenting the readiness packet as Wednesday's reviewed deliverable; make no deployment, independence, or backup claim until F1's scoped collection returns actual receipts. Charter ratification, patient launch, 047 landing, writer/reset design, 48/96 activation, and report schedule remain operator-owned and untouched.