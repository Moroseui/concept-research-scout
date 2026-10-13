# 13B execution plan

Updated 13 October 2026, 21:38 UTC. New experiments first. The scientific author writes each notebook; Claude reviews it. Every arm requires actual nnU-Net trainer construction and a training iteration before full delivery.

| Order | Arm × folds | Venue | State and next step |
|---|---|---|---|
| First, session 1 | A1_multiwin × 0–4 | **Partho on Colab**, default runtime, A100 | Returned check failed NumPy provenance before trainer construction. Exact author correction recovered; all six CPU tests passed. Scientific REVISE remains; corrected synthetic-check package is APPROVED and delivered. Await actual A100 evidence, then scientific review. |
| First, session 2 | A1_pnormct × 0–4 | **Partho on Colab**, default runtime, A100 | Stalled after epoch86; corrected worker/watchdog/early-login file delivered. Resume verified checkpoint, expected next_epoch85; do not duplicate old runtime. |
| Next | A1_pnorm_v2 × 0–4 | **Partho on Colab**, default runtime, A100 | Actual A100 trainer PASS accepted; old all-fold notebook reported running; corrected operational file delivered. Switch after fresh checkpoint, preserving science and results. |
| Then | A1_L × 0–4 | **Partho on Colab**, default runtime, A100 | Author3/reviewer3 complete, scientific REVISE. Preparation-only notebook delivered to create authentic ResEncL plans. Then actual trainer/resume/memory evidence and baseline metric review; no full release or memory-fit claim. |
| Parked | A1_repeat × 0–4; A1_repeat2 × 0–4 | Partho on Colab later | New arms must have results first. Saved preprocessing stays; per-fold files remain parked. |
| Held | A1_zscore × 0–4; A1_histeq × 0–4 | No run | Coverage-source provenance unresolved. |

**How to run:** two parallel sessions when capacity permits, one arm per session. Each full notebook preprocesses once, then trains/scores five folds sequentially for 250 epochs. Re-running resumes the current checkpoint and verifies/skips completed folds. No settings changes, per-fold files, balance prompts or supervised segments. Hashes and exact development99/excluded49 membership fail closed; results stay private in separate built-in Drive folders.

**Current files:** use the [corrected resume files and full hashes](COLAB_RESUME_20261013.md) for pnormct and pnorm_v2; L has an updated preparation-only early-login file. All prompts and browser capture must finish in the first cell, before expensive work. Wait for the exact ready line. Older files are preserved but should not be used for new sessions. The [multiwin trainer-check early-login/isolation update](MULTIWIN_TRAINER_CHECK_20261013.md) is reviewed and delivered.

**Time and units:** returned pnormct/v2 timing is190-196seconds/epoch with about157seconds loader wait and2workers. The old14hour estimate is invalid: a five-fold arm is about67-68hours /454-460CU at that rate. The reviewed resource fix chooses12workers on the observed12CPU runtime; actual new speed is unmeasured, and repeated Drive input hashing remains a possible bottleneck. At Sprint12's36seconds/epoch, five folds would take12.5training hours /84.63CU before overhead; that is a reference, not a measured changed-arm projection. The original1,001units buy147.86A100hours at6.77CU/hour. Partho manages top-ups; units do not limit the plan.

**Comparison:** use Sprint12 A1 provisionally. Small differences are not interpretable without a later Colab repeat. Analyse placement versus amount, size, region and fragmentation.

**Parallel work:** Partho can resume pnormct and switch pnorm_v2 independently using the corrected files. Multiwin's parent-mounted, isolated-worker trainer check is reviewed and delivered; actual Colab support is unmeasured and fails closed before GPU work if unavailable. L preparation uses upfront logins and still needs genuine plans and an actual A100 check. Item6, Idea2 and smoothing remain accepted. Meeting preparation is accepted but actual private input/admission and image QC remain. Defer unrelated sandbox/rotation engineering.

**Timing diagnostic:** Modal GPU RunA versus more CPU/augmentation workers in RunB remains approved within $25; run B first if necessary. No GPU result yet. The old timing review's admission/authority issue remains unresolved; it may not borrow the new purpose-specific calls and does not block Colab.

**Money:** operator approved 128→140 scientific calls: four for returned multiwin/pnorm_v2 evidence, four for L, four for meeting. Batch140 is installed;134 calls used, with 2 meeting, 2 returned-Colab and 2 L slots used; 2 meeting, 2 returned-Colab and 2 L remain. Daily50, per-run20 and GPU caps stay unchanged. Non-Colab stage1: $24.487001 billed + $91.029622 retained reservations = $115.516623/$150; $25 timing sub-cap, $1,200 projection gate and $1,275 total unchanged. Colab is unmetered. [Detailed status and audit](STATUS.md).
