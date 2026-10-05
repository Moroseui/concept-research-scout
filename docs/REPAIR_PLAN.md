# Autonomous research system: repair plan

Prepared 2026-09-24 from the independent inspection (Claude Code on the laptop and server, plus a Cowork source review of the public repository).

The goal is unchanged: an agent-drivable, human-readable research system that proposes, runs, analyzes and records experiments verifiably. This plan keeps the repository and the parts that work. It changes the four things that stop the system from producing research.

## Revised sequencing (v2, after Astra's review; supersedes section 4's order)

Make one change at a time, check it, then decide on the next.

- **(a) Housekeeping.**
  1. Back up everything first, including uncommitted and untracked work, to a private location, and verify that the backup can be restored.
  2. Disable the stale `6b55507` timers.
  3. Deduplicate the `claude` binaries. Keep one copy of each distinct version (by sha256) and keep every receipt binding resolvable, for example with hardlinks.
  4. List the failed units with a cause for each, without fixing them.

  This step does not change how the system works.
- **(c) Context budget** (M1), with the obligation tests below.
- **(d) Sprint 10 end to end through the manual executor lane** (M2).
- **(b) GPU proof: deferred by operator decision (2026-09-24) until (a), (c) and (d) pass.** The manual executor lane covers execution until then. Meanwhile:
  - the executor interface (`submit`, `status`, `collect`) is built for the manual lane, so a GPU backend can be added later without engine changes
  - new notebooks are written to run headless: parameters in one cell, no interactive steps, and paths set by configuration rather than a Drive mount

  When (b) starts, rerun sprint 8 r4 on Modal. Before running:
  - set the spending limit
  - decide which data may be uploaded (development patients only; locked patients never)
  - pin source, split, preprocessing, environment and metric
  - predeclare the tolerance from the measured sprint 8 spread (seed ≤0.001, split about 0.004), for example: the mean Dice for each recipe is within ±0.005 of the Colab run, with identical partition fingerprints

- Later: unattended GPU runs (M3), 48-hour operation (M4), generality check (M5).

## Amendments from Astra's review (2026-09-24)

1. **Diagnosis wording.** GPU absence blocks *experiments*. It does not explain why CPU and non-execution stages on `c703d89` stall; context growth and process overhead explain that. Classify each defect as a deployment defect or a workflow defect. The review159 request was withdrawn (V256), and no operator decision is pending.
2. **Preserve guarantees, not modules.** These four guarantees must survive any archiving, each with at least one focused test that still passes:
   - admission: no unauthorized or duplicate starts; stops and budgets are enforced
   - protected intake: untrusted input never becomes authority
   - recovery: an uncertain submission is reconciled, never rerun
   - deployment verification: installed code matches reviewed code

   Nothing is archived without a module-level keep/archive list. A guarantee without a test doesn't count as preserved.
3. **Every executor uses `job_store` and the accounting** (manual, Modal, CPU). Notebook fingerprints bind inputs, split, code and configuration.
4. **Deploy.** Deploy a pinned release tag, reconcile in-flight jobs before restarting, and keep a one-command rollback to the previous tag.
5. **Review outcome rule.**
   - An unresolved *blocker* after round 2 ends in defer, reject or escalate. It never proceeds automatically.
   - *Advisory* items proceed and are recorded.
   - An escalation is a one-paragraph decision request.
   - New evidence can establish a blocker, but only within the fixed categories.
6. **New blocker category:** invalid execution authority or provenance. This covers unauthorized runs, uncertain or duplicate dispatch, and results that can't be shown to belong to the approved run. Deterministic checks on receipts and installs stay in place, even where separate model reviews are removed.
7. **Context completeness (main risk).**
   - `STATE.md` and `POLICY.md` are *derived* summaries.
   - Open obligations (stops, adverse findings, protocol amendments, constraints) are structured records with ids and scope tags. Every stage receives all open obligations in its scope, never a paraphrase.
   - Archived evidence stays retrievable by id through a read tool; a hash alone is not enough.
   - Required tests:
     - Irrelevant history appended → the stage input size is unchanged.
     - One applicable stop, adverse finding or amendment added → it appears in the correct stages and changes their behavior.
     - The 200k-character cap alone proves neither completeness nor correctness.

## 1. Diagnosis: four structural causes

| # | Problem | Evidence | Why patching hasn't worked |
|---|---|---|---|
| 1 | **No unattended GPU route.** The server cannot drive Colab. | Two 5-second timers report `00-colab-blocked` on every run. The server job queue has been empty since 09-11. | Every downstream stage waits on an execution step that can't happen. |
| 2 | **Inputs grow with history.** | `scout.py:218-236` includes the whole append-only `decisions.md`. `hosted_context.py` includes 9–13 governance documents in full plus a 418 K-character change history. The largest input is 1.02 M characters, and three stages are already refused. | Each fix adds history, so the margin always shrinks. |
| 3 | **Review has no stopping rule, and its scope is too wide.** | 287 reviewer sessions and 1 research transition since 09-07. Review count reached about 160. Each review copies a 289 MB binary (66 GB total). | Receipts, installs and handoff notes are all reviewed, and every review produces more records to review. |
| 4 | **Deployment and development sprawl.** | Three source versions run on the server, 42 units have failed, there were 17 pause/resume cycles (one per install), 137 worktrees exist, 1,119 RESTART notes were written, and the work is 277 commits ahead of any remote. | Each install is a reviewed, paused event, so a small change costs a full cycle. |

A fifth, lower-priority issue affects generality. The "general" engine hard-codes ISLES paths: `hosted_context.py` names `campaigns/isles24-pilot`, `charters/isles24` and `P001/SPEC.md`.

## 2. Target design (small)

- **Unit of work: the run spec.** It is what your sprint notebooks already are: a notebook plus parameters, pinned input hashes, declared outputs (`completion.csv`, summaries, figures), a validator and a SMOKE mode. The system writes it, reviews it once, executes it, validates the outputs, interprets them and updates the project state. This is also how the notebooks come *inside* the system.
- **Executors are pluggable.** The engine only calls `submit(run_spec) → run_id`, `status(run_id)` and `collect(run_id) → outputs`.
  - `manual`: the system writes the notebook, you run it in Colab and drop the outputs in an import folder. Works today with no new infrastructure.
  - `gpu-api`: headless execution on a GPU service (section 5).
  - `cpu-local`: small jobs on the server itself.
- **Context comes from state, not history.**
  - `STATE.md` per project, rewritten after every transition and versioned in git, around 5–8 K tokens. It holds the question, the incumbent result, open obligations, active constraints (the locked test set), and the last few decisions with links.
  - `POLICY.md`, about 2 K tokens, condenses the governance documents. Full documents are cited by sha256, not pasted in.
  - Only log entries tagged with the current run or idea id are included, up to a capped count. `decisions.md` stays as the complete archive and is never included in full.
  - Hard cap of 200,000 characters per stage input, enforced by a test.
- **Review with a stopping rule.** Claude reviews happen at three points only: (a) a run spec before GPU spending, (b) a result interpretation, (c) an engine code PR.
  - At most two rounds per item.
  - A blocker must be one of: test-set or leakage violation; code that doesn't match the spec; wrong metric or statistic; private data exposure or secret leak; over budget. Everything else is advisory and gets recorded.
  - After round 2, the driver either proceeds with the objections recorded or sends you a one-paragraph decision request.
  - No reviews of receipts, installs, handoff notes or records.
- **Driver loop.** Read `STATE.md`, choose one action (propose run spec / launch approved spec / collect and validate / interpret / propose next), do it, rewrite `STATE.md`, commit. Daily budget for GPU dollars and model calls. The nightly report is the `STATE.md` diff plus new results, posted as a GitHub issue.
- **Deploy.** The server runs exactly one tagged release pulled from git. Deployment is one script (pull, then restart) gated by green CI, with no pause/resume cycle per install.

## 3. What to keep and what to archive

Archive means moving to `archive/`, not deleting.

**Keep:**
- `job_store.py` (leases, deduplication, the ambiguous-dispatch block, which is exactly what prevents duplicate runs)
- `experiment_registry.py` validators
- ledger accounting
- run fingerprints and resume validation from the sprint notebooks
- the scout/critique/debate idea stages
- the test suites

**Archive:** handover, admission, protected-intake, recovery, fixture and acceptance layers that exist only to prove the deployment itself. Codex lists each module with a one-line keep or archive reason before moving anything.

## 4. Milestones and acceptance criteria

These run in order. Each ends with a report of one page or less containing acceptance evidence only.

**M0: Clean baseline**
- One release on the server, and the stale `6b55507` timers removed.
- Zero failed units, or each remaining one explained in one line.
- Duplicate `claude` binaries removed from the review directories (inputs and outputs kept), with `df -h` before and after.
- All code pushed to a **private** remote. Make the GitHub repo private or use a new private repo, because private evidence lives nearby and phenotype files leaked once before.
- Worktrees consolidated to one active checkout, with the rest archived.
- One `CURRENT.md` handoff file, overwritten each session, and no new RESTART files.

**M1: Context budget**
- `STATE.md` and `POLICY.md` exist for the ISLES project.
- The stage builders in `scout.py` and `hosted_context.py` use them.
- Test: appending 1,000 synthetic decisions to `decisions.md` changes every stage input by 0 bytes.
- Test: every stage input is under 200,000 characters.
- The three currently refused stages now fit.

**M2: Manual executor lane (brings the notebooks inside)**
- Sprint 10 (tree vs U-Net comparison, already designed) goes through the system end to end:
  1. run spec committed
  2. one review, two rounds at most
  3. notebook emitted
  4. you run it in Colab
  5. outputs dropped in the import folder
  6. validator passes
  7. interpretation written and reviewed
  8. `STATE.md` updated
  9. nightly report posted
- Model sessions, review rounds and elapsed time are recorded.

**M3: Unattended GPU executor.** This needs your backend decision (section 5).
- One real run spec is launched by the driver while the laptop is closed.
- The outputs are collected and validated, the interpretation is written, and the report is posted.
- There is no duplicate run after a forced restart during the run.

**M4: 48-hour unattended operation**
- At least two completed research transitions without intervention.
- Budget respected, and a nightly report each night.

**M5: Generality check**
- ISLES specifics move out of engine code into `projects/isles24/project.yaml`: paths, locked sets, metrics, executor, budget.
- A toy second project (for example, a public tabular dataset) runs through M2's lane with zero engine code changes.

Standing metrics for every milestone report: completed research transitions, model sessions, review rounds, human interventions and GPU dollars.

## 5. GPU backend options for M3

| Option | Fit | Notes |
|---|---|---|
| **Modal** | Python-native, per-second billing, easy to call from the server | Starter plan includes $30/month in credits. A T4 costs about $0.59/hour, and A100/H100-class GPUs cost a few dollars an hour. Researchers can apply for up to $10k in credits. The data must be copied to a Modal Volume. |
| **Colab Enterprise** (Google Cloud) | Closest to the current notebooks | Supports headless `NotebookExecutionJob` via `gcloud colab executions create`. Needs a GCP project with billing, a runtime template and a GCS bucket for outputs. Drive paths would change to GCS. |
| **Kaggle notebooks** | Free weekly GPU quota, API push | Smaller GPUs and quota limits. The data must be uploaded as a private Kaggle dataset. |

Recommendation: Modal, and apply for research credits. Label blindness can then be enforced **mechanically**: the 25 fresh test patients and the 24 still-sealed ones are simply never uploaded to the execution volume.

## 6. Development process rules for Codex

- The success metric is completed research transitions per week. Infrastructure work must name the research step it unblocks.
- Small PRs to a branch, with CI as the gate and one Claude review per PR (two rounds at most).
- Every change to shared server state goes through the single deploy script.
- Hard controls that stay unchanged:
  - locked test patients
  - no patient data on any public remote
  - spending caps
  - secrets handling
  - your sign-off on merges to main


## Active batch and M4 amendment (2026-09-27)

`AUTONOMY_BATCH_2026-09-27.md` is the active M0?M6 sequence, superseding the historical milestone ordering above. Its M4 successor-contract amendment and verbatim operator record apply. Preserve old H2/controller work read-only; do not resume or reuse its formal adoption machinery. No old units/state changes are authorized by the batch.
