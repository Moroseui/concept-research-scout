# 13B execution plan

Updated 13 October 2026, 13:32 UTC. New experiments first. The scientific author writes each notebook; Claude reviews it. Every arm requires actual nnU-Net trainer construction and a training iteration before full delivery.

| Order | Arm × folds | Venue | State and next step |
|---|---|---|---|
| First, session 1 | A1_multiwin × 0–4 | **Partho on Colab**, default runtime, A100 | Returned check failed NumPy provenance before trainer construction. Exact author correction recovered; all six CPU tests passed. Scientific REVISE remains; corrected synthetic-check package is APPROVED and delivered. Await actual A100 evidence, then scientific review. |
| First, session 2 | A1_pnormct × 0–4 | **Partho on Colab**, default runtime, A100 | Full notebook delivered after real trainer PASS; last reported running. Do not duplicate it. |
| Next | A1_pnorm_v2 × 0–4 | **Partho on Colab**, default runtime, A100 | Actual A100 trainer PASS accepted; unchanged reviewed all-fold notebook delivered and reported running. |
| Then | A1_L × 0–4 | **Partho on Colab**, default runtime, A100 | Author3/reviewer3 complete, scientific REVISE. Preparation-only notebook delivered to create authentic ResEncL plans. Then actual trainer/resume/memory evidence and baseline metric review; no full release or memory-fit claim. |
| Parked | A1_repeat × 0–4; A1_repeat2 × 0–4 | Partho on Colab later | New arms must have results first. Saved preprocessing stays; per-fold files remain parked. |
| Held | A1_zscore × 0–4; A1_histeq × 0–4 | No run | Coverage-source provenance unresolved. |

**How to run:** two parallel sessions when capacity permits, one arm per session. Each full notebook preprocesses once, then trains/scores five folds sequentially for 250 epochs. Re-running resumes the current checkpoint and verifies/skips completed folds. No settings changes, per-fold files, balance prompts or supervised segments. Hashes and exact development99/excluded49 membership fail closed; results stay private in separate built-in Drive folders.

**Files now running:** `13B_A1_pnormct.ipynb` and `13B_A1_pnorm_v2.ipynb`, both reported running by Partho. Exact reviewed hashes are in [STATUS](STATUS.md). Leave both alone. Full outputs return through separate built-in private Drive folders and are verified before scientific analysis. The earlier multiwin check failed before trainer construction; do not repeat it unchanged. Corrected check delivered: [morning instructions](MULTIWIN_TRAINER_CHECK_20261013.md). It takes10-25 minutes; Partho can run it after waking.

**Time and units:** Pnormct and pnorm_v2 print about14hours /94.78CU. Multiwin's provisional estimate is 15–20 hours; L's is 35–45 hours, with automatic resume across disconnects. At Sprint12's measured 36 seconds/epoch, five folds require 12.5 training hours / 84.63 CU before overhead. That reference would give 100 hours / 677 CU for 40 fits, but it is not a measured projection for the changed arms. At 6.77 CU/hour, the original 1,001 units buy 147.86 A100 hours. Partho manages top-ups; units do not limit this plan. Replace estimates with returned steady-state timings.

**Comparison:** use Sprint12 A1 provisionally. Small differences are not interpretable without a later Colab repeat. Analyse placement versus amount, size, region and fragmentation.

**Parallel work:** pnormct and pnorm_v2 remain reported running. Multiwin's corrected check is ready; L's [preparation-only notebook](L_PREPARATION_20261013.md) is ready next. Its runtime is unmeasured and it trains nothing. L source evidence is ready for scientific baseline-metric judgment. Item6, Idea2 and smoothing are accepted. Meeting preparation is approved with12synthetic tests; actual input/admission bindings, source access and independent image QC remain. No model call is running. Defer unrelated sandbox/rotation engineering.

**Timing diagnostic:** Modal GPU RunA versus more CPU/augmentation workers in RunB remains approved within $25; run B first if necessary. No GPU result yet. The old timing review's admission/authority issue remains unresolved; it may not borrow the new purpose-specific calls and does not block Colab.

**Money:** operator approved 128→140 scientific calls: four for returned multiwin/pnorm_v2 evidence, four for L, four for meeting. Batch140 is installed;134 calls used, with 2 meeting, 2 returned-Colab and 2 L slots used; 2 meeting, 2 returned-Colab and 2 L remain. Daily50, per-run20 and GPU caps stay unchanged. Non-Colab stage1: $24.487001 billed + $91.029622 retained reservations = $115.516623/$150; $25 timing sub-cap, $1,200 projection gate and $1,275 total unchanged. Colab is unmetered. [Detailed status and audit](STATUS.md).
