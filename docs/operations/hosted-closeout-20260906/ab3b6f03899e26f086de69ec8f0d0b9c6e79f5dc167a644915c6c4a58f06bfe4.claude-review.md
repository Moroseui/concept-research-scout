# Cross-family operational review — 2026-09-06 supervised cycle

**Verdict:** The receipt chain is internally consistent and the synthetic cycle (trigger → selection → dispatch → report) is plumbed end-to-end, but the evidence does **not** demonstrate acceptance of the *reporting-pin* implementation, and the deployed-service properties contradict the hardening story. Concrete items below. No main-merge approval is implied, and all reserved decisions (patient work, 047, charter ratification, unattended activation, publication grants) remain untouched by this review.

## What the evidence actually supports

- All five verified events bind attempt_id/job_id/source correctly, carry valid console hashes, and the artifact hash `776c3a10…` matches the fixed synthetic payload. The failure job (20) and the colab block (00) behave as designed.
- The report's counts (4/1/1/0) match the job rows, and the new provenance line correctly distinguishes the reporting pin `e7bff179…` from the execution pin `6b555075…`.
- Astra's selection of `41-closeout-followup` was validated against the single pre-declared eligible task; note this is a **constrained confirmation, not an autonomous decision** — acceptable as plumbing evidence only, and the prompt honestly says so.

## Concrete defects

1. **Capability bounding sets are effectively unrestricted.** Both services carry the full capability set (`cap_sys_admin`, `cap_sys_module`, `cap_sys_ptrace`, `cap_dac_override`, …). `NoNewPrivileges=yes` plus non-root users mitigates this, but the units do not implement the claimed least-privilege posture. `PrivateDevices=no` and `ProtectKernelTunables=no` compound this.
2. **Both services were `inactive`/`dead` at snapshot time.** The receipts prove jobs ran, but nothing in the packet ties that execution to these systemd units — the tick/worker for job 41 evidently ran some other way (manual invocation or a timer not shown). "Deployed service properties" therefore do not attest the actual execution path.
3. **`atomic()` in `remote_supervisor.py` never fsyncs the containing directory** after `os.replace`, while `hosted_cycle.immutable` and the new `operations_report.immutable` do. Request and outcome files can be lost on crash despite the "durable events" claim. Reconcilable via the DB, but inconsistent with the stated durability standard.
4. **Version-skew hazard is live, not hypothetical.** The new worker emits version-2 receipts with a `failure` object; the old controller's `validate_receipt` (the one at the execution pin, which actually ran) rejects anything with `version != 1`. Any mixed deployment of new worker against old controller fails closed on every job. This needs an explicit migration/compatibility note before the new pin is activated.

## Acceptance gaps

- **Every verified event is version 1, produced by the old execution-pin code.** The reporting pin's changes — the v2 failure taxonomy, `validate_receipt` v2 branch, granular block reasons, git-env hardening in `checked_source`, and the report provenance line's downstream consumers — have zero execution evidence here. Job 20's reason is the generic `SYNTHETIC_WORKER_FAILED_OR_TIMED_OUT`, confirming the new taxonomy was never exercised. No test results are supplied either.
- **`hosted_cycle.py`, `hosted_review_recovery.py`, and `hosted_cycle_reconcile.py` exist only at the reporting pin**, so the recovery and reconcile paths have no receipts at all — only source text.
- **`git_publication.py` at the reporting pin adds a second grandfathered fixture hash** (`159246c8…`, "reviewed at 460deab"). That widens the case-level-record exemption; the claimed review is asserted in a comment, not evidenced in this packet. Independent confirmation of that review should precede any publication using the new pin.
- **Wake backlog is invisible in the report.** Each completion inserts a `PENDING_AUTH` wake; only the job-40 wake can have been processed by this cycle, leaving at least four pending, and neither the daily report nor the packet's job rows surface them.
- **Astra model identity remains unverified** for the continuation and disposition calls (the receipt honestly records this); only the Claude call proves its resolved model. Fine for now, but it is an open gap for any claim of cross-family authorship.

## Suggested next actions (through existing routes)

Run one cycle against a checkout at the reporting pin so the v2 receipt path, granular failure reasons, and provenance line are exercised with real receipts; capture service `ActiveState=active` evidence (or explicitly document manual invocation as the sanctioned path); and either tighten `CapabilityBoundingSet` or amend the operating direction to state the actual mitigation is NNP + non-root users. None of this requires or grants any reserved authority.