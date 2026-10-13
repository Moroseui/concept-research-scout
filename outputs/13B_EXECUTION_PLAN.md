# 13B execution plan

Updated 13 October 2026, 09:52 UTC. New experiments first. The scientific author writes each notebook; Claude reviews it. Every arm requires actual nnU-Net trainer construction and a training iteration before full delivery.

| Order | Arm × folds | Venue | State and next step |
|---|---|---|---|
| First, session 1 | A1_multiwin × 0–4 | **Partho on Colab**, default runtime, A100 | Returned check failed NumPy provenance before trainer construction. Author correction completed; exact saved output recovery is under implementation review, then scientific re-review. No trainer PASS yet. |
| First, session 2 | A1_pnormct × 0–4 | **Partho on Colab**, default runtime, A100 | Full notebook delivered after real trainer PASS; last reported running. Do not duplicate it. |
| Next | A1_pnorm_v2 × 0–4 | **Partho on Colab**, default runtime, A100 | Actual A100 trainer PASS accepted; unchanged reviewed all-fold notebook delivered and reported running. |
| Then | A1_L × 0–4 | **Partho on Colab**, default runtime, A100 | Review2 requests exact A100 trainer/resume/memory evidence and baseline binding. Baseline files are authenticated; scientific binding remains. No memory-fit claim or full release. |
| Parked | A1_repeat × 0–4; A1_repeat2 × 0–4 | Partho on Colab later | New arms must have results first. Saved preprocessing stays; per-fold files remain parked. |
| Held | A1_zscore × 0–4; A1_histeq × 0–4 | No run | Coverage-source provenance unresolved. |

**How to run:** two parallel sessions when capacity permits, one arm per session. Each full notebook preprocesses once, then trains/scores five folds sequentially for 250 epochs. Re-running resumes the current checkpoint and verifies/skips completed folds. No settings changes, per-fold files, balance prompts or supervised segments. Hashes and exact development99/excluded49 membership fail closed; results stay private in separate built-in Drive folders.

**Files now running:** `13B_A1_pnormct.ipynb` and `13B_A1_pnorm_v2.ipynb`, both reported running by Partho. Exact reviewed hashes are in [STATUS](STATUS.md). Leave both alone. Full outputs return through separate built-in private Drive folders and are verified before scientific analysis. The earlier multiwin check failed before trainer construction; do not repeat it unchanged. Corrected check expected after author/review, roughly45-90minutes subject to findings.

**Time and units:** Pnormct and pnorm_v2 print about14hours /94.78CU. Multiwin's provisional estimate is 15–20 hours; L's is 35–45 hours, with automatic resume across disconnects. At Sprint12's measured 36 seconds/epoch, five folds require 12.5 training hours / 84.63 CU before overhead. That reference would give 100 hours / 677 CU for 40 fits, but it is not a measured projection for the changed arms. At 6.77 CU/hour, the original 1,001 units buy 147.86 A100 hours. Partho manages top-ups; units do not limit this plan. Replace estimates with returned steady-state timings.

**Comparison:** use Sprint12 A1 provisionally. Small differences are not interpretable without a later Colab repeat. Analyse placement versus amount, size, region and fragmentation.

**Parallel work:** item6, Idea2 and smoothing interpretations are accepted. Meeting author3/reviewer3 completed,12synthetic tests PASS and preparation APPROVE. Real panels still require approved private inputs/admission and independent image QC. The multiwin continuation is installed. Its author completed the correction; a hash-bound output-size recovery is under implementation review. Author sandbox and operator-rotation infrastructure remain deferred behind these results.

**Timing diagnostic:** Modal GPU RunA versus more CPU/augmentation workers in RunB remains approved within $25; run B first if necessary. No GPU result yet. The old timing review's admission/authority issue remains unresolved; it may not borrow the new purpose-specific calls and does not block Colab.

**Money:** operator approved 128→140 scientific calls: four for returned multiwin/pnorm_v2 evidence, four for L, four for meeting. Batch140 is installed;131 calls used, with 2 meeting and 1 returned-Colab slots used; 2 meeting, 3 returned-Colab and 4 L remain. Daily50, per-run20 and GPU caps stay unchanged. Non-Colab stage1: $24.487001 billed + $91.029622 retained reservations = $115.516623/$150; $25 timing sub-cap, $1,200 projection gate and $1,275 total unchanged. Colab is unmetered. [Detailed status and audit](STATUS.md).
