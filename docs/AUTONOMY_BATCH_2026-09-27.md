# Autonomy batch: operator instructions (2026-09-27)

**Goal:** full autonomy. The system runs research on the server, including CPU and GPU execution, with no manual Colab runs. It chooses its next run from an approved backlog and reports nightly, stopping only when a real decision is needed.

**Mode:** work through the milestones in order. After each milestone, write a report of one page or less to `AUTONOMY_PROGRESS.md` and **continue without waiting** unless a stop condition below applies. Plan of record: `docs/REPAIR_PLAN.md`, with its amendments and prior operator decisions, which remain in force.

## Standing rules

**Stop and wait for me only for:**

1. **Old units and old state.** Anything that touches the 18 held old units or the old state.
2. **Security controls.** Any change that weakens isolation or sandboxing, touches privacy, credentials or secrets, or alters AppArmor beyond the approved scoped profile.
3. **Locked patients.** Any access to the 25 final-evaluation or 24 reserve patients, or uploading them anywhere.
4. **Spending and calls.** Spending or model calls beyond the caps below.
5. **Blocked reviews.** A review blocker still unresolved after 2 rounds.
6. **Failed invariants.** For example, old-state drift or a failed hash or provenance check.
7. **Uncertain calls.** An uncertain model call.
8. **Things only I can do.** Accounts, tokens, logins, billing.
9. **Merges to main.** Any merge to main.

Everything else: fix, record and continue. For a reversible, confined failure, fix it and continue. After the same failure happens twice, stop.

**Reviews are automated.** Build step M0 first. After that, engine-code and deployment changes get an independent Claude review through the automated reviewer instead of waiting for me: at most 2 rounds, fixed blocker categories, and the report is saved verbatim. Scientific stages keep their own in-lane reviews.

**Caps, until I raise them:**

- Model calls: at most 30 in total across M2–M6 acceptance runs, at most 8 per research run, and at most 20 per day.
- GPU spending (Modal): at most $50 in total until M6 is accepted, and at most $15 per run. Every run gets an estimate before launch, and a run that would exceed its estimate is refused.
- One run at a time.

**Freeze:** build only what these milestones require.

## Milestones

**M0: Automated independent reviewer.**
- A tool that runs Claude Code headless, read-only (plan mode, with edits and project-code execution denied), from its own dedicated login, against a review folder, using a fixed prompt template: blocker categories, verdict heading, source and runtime binding.
- Codex cannot edit the report, and the report is stored with its hash.
- **Acceptance:** re-review one already-approved packet (RC6) and one packet with a planted defect. The first gives APPROVE and the second gives CHANGES REQUIRED.

**M1: Fix batch.**
- Startup cleanup of leftover per-call token copies.
- Commit the format-repair record and the original interpretation.
- Deduplicate identical host-refusal records.
- The installer checks all host prerequisites before its first write.
- Support newer Claude package layouts.
- A supported, recorded post-start re-execution path for infrastructure failures, keeping the one-retry limit.
- Promote with the versioned promoter, and run both server suites.

**M2: Server CPU executor (no more Colab for CPU work).**
- CPU runs execute on the server itself, inside the sandbox, under `partho`.
- The input data, i.e. the feature cache and the prior run outputs needed, is copied to the server's private storage with hash verification. **Development patients only**: the 25/24 locked patients are never copied.
- **Acceptance:** rerun the Sprint 10 known case on the server CPU. The outputs must be byte-identical to the accepted tables, with no Colab involved.

**M3: GPU executor (Modal).**
- The executor submits, monitors and collects a run on Modal. It is idempotent, and an uncertain submission is never resubmitted.
- The data goes to a private Modal volume with hash checks, again with no locked patients.
- The per-run cost estimate and cap are enforced.
- The Modal token lives only in the executor's private credential location, outside every model sandbox. Model calls never see a spending credential, and only reviewed, approved code is submitted.
- **Acceptance:** a short GPU reproducibility smoke on a known case, for example one Sprint 9 U-Net fold at reduced epochs compared against its predeclared tolerance, within $10.
- **Needs me:** Modal account token and billing. Ask me at the start of the batch, not mid-way.

**M4: Closing the loop.**
- An operator-approved research backlog file, `BACKLOG.md`, which only I edit.
- An **implementation stage**: an author writes the experiment code or notebook from the approved spec, a reviewer checks it, and the executor runs it.
- After each interpretation, the driver may start the next run **only** from a backlog item that matches the reviewed next decision. Otherwise it stops with a one-paragraph proposal for me.
- **Acceptance:** one new CPU experiment chosen from the backlog runs end to end.

**M5: Operation.**
- A scheduler that runs the driver unattended.
- A nightly report at 21:00 America/New_York, posted as a GitHub issue or comment in a **private** repo. It covers runs, results, calls, spending, blocks and pending decisions.
- Phone commands through that issue: pause, resume, approve decision X. Only my GitHub account can issue them.

**M6: 24–48 hour unattended test** on real backlog items, with the laptop off. Report at the end.

## Initial backlog, for BACKLOG.md

1. **Sprint 12 tree/CTA ablations (CPU).** First apply the Sprint 12 notebook review repairs:
   - #5 completion status written before validation
   - #6 volume-calibration models not saved
   - #7 completion and metric-reuse checks
   - #10 version overrides
   - the reporting-label fixes
2. **Sprint 12 nnU-Net arms (GPU),** after M3. Apply review repairs #1–#4 (checkpoint recovery, run identity, the A0 plan transfer, geometry checks) and #8–#9. Smoke runs first, with the measured time and cost before any full folds.

Keep the 25 final-evaluation patients locked throughout. All results are development results.


## Operator amendment: M4 successor contract (2026-09-27)

The original batch above is preserved verbatim. The subsequent operator decision is recorded verbatim in `operator-decisions/20260927-m4-successor-contract.txt`.

- A successor can consume prior outputs only when validated, accepted, and matching the declared cohort, split, feature/cache identity and hashes; otherwise refuse.
- DEFER and proposal-only outcomes never authorize a start. A reviewed permitting next decision must match an operator-approved backlog item.
- M4 acceptance includes refusal tests for both requirements.
- Implement in the new lane. H2 and the old controller remain archived/read-only; no formal H2 adoption machinery is required.

## Observed-outage amendment (operator, 2026-09-28)

M1 additionally implements DNS plus HTTPS checks for each required provider before any model-call reservation or job submission. A failed network preflight refuses without charge. M5 nightly reporting includes connectivity status. Source: operator-decisions/20260928-network-outage.txt and its SHA256 binding. The outage/reboot is reported with unknown cause; do not diagnose credentials or infer authorization to alter host networking. Remote commands reuse a single ControlMaster/ControlPersist connection. Post-reboot old-state/units, RC6 units, policy and private credential metadata must pass before M0 continues.
