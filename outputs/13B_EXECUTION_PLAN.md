# 13B execution plan

New experiments first. Old repeat and multiwin notebooks are held after a real trainer-initialization failure; saved preprocessing remains. No corrected file is ready yet.

| Order | Arm and folds | Venue and owner | Release condition |
|---|---|---|---|
| First, session 1 | A1_multiwin, 0-4 | **Partho on Colab**, default runtime, A100 | Parked after mechanical review failure at run20; corrections, real integration and scientific approval still required |
| First, session 2 | A1_pnormct, 0-4 | **Partho on Colab**, default runtime, A100 | Pure synthetic PASS; scientific review running; actual trainer iteration still required |
| Next | A1_pnorm_v2, 0-4 | **Partho on Colab**, default runtime, A100 | Same checks; release as soon as ready |
| Then | A1_L, 0-4 | **Partho on Colab**, default runtime, A100 | Same checks plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2, 0-4 each | Partho on Colab later | New arms must have results first |
| Held | A1_zscore and A1_histeq, 0-4 each | No run | Coverage-source provenance unresolved |

Each arm gets ONE preconfigured file: preprocess once, train/score folds 0-4 sequentially at 250 epochs, verify/skip completed folds and resume the current checkpoint. No settings to change or per-fold files. Mount Drive, verify frozen hashes and development/exclusion membership, keep results private in distinct built-in arm/fold paths, and print subprocess errors. Re-run the same file after disconnection.

The author writes scientific code and the real synthetic integration fixture; the operator supplies execution infrastructure. Actual nnU-Net trainer construction and at least one training iteration per arm are required before delivery. Static/mocked checks are insufficient. A100 memory-fit evidence is additionally required for L. Server CPU handles suitable synthetic tests and saved-output analysis; a reviewed Modal GPU route may run the actual trainer fixture inside existing caps. No new GPU reservation has been made for it.

When both first arms are released, run two Colab sessions in parallel, each processing its five folds sequentially. Exact reviewed filenames, hashes and private result destinations will accompany each release; open, choose A100, Run all. No human action now.

At Sprint 12's measured 36 seconds/epoch, five folds of 250 epochs imply 12.5 training hours before preprocessing, validation and checkpoint overhead, or 84.63 CU at 6.77 CU/hour. This is a reference, not a measurement for the new arms. Multiwin's prior provisional estimate is 15-20 hours/arm (101.55-135.40 CU); L's 35-45-hour estimate remains unvalidated. Replace these with observed steady-state timing. Automatic resume is essential if an arm outlasts a Colab session. The original 1,001 units equal about 147.86 A100 hours at that burn rate, but unit balance does not limit this plan; Partho manages purchases.

Compare each arm provisionally against Sprint 12 A1. State plainly that small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation. The system ingests private Drive metrics, timing and run summaries as they arrive. No bulk laptop copy is resumed.

In parallel: the next saved-output analysis and private meeting preparation have author intakes ready. The installed model-call guard currently serializes calls; do not bypass it. Item 6 and Idea 2 are accepted, with Idea 2's reviewer inspection limitation documented. Timing is deferred. Approved batch 128, daily 50 and run 20 remain in force; other questions need normal scoped admission. Item 4 non-Colab stage 1 is $150, total $1,275, projection gate $1,200, and timing $25 inside stage 1.

Pnormct author 2 completed and its corrected notebook passed all five controller synthetic test groups, including five execution-module tests with none skipped. These are pure-function tests, not real training. Notebook hash30bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6; exact module33153177657c1f2a3383bcd50fffb393a571514c3363f7ef2c24f131d48251f2.

Scientific review 1 is RUNNING, confirmed at 11:55 UTC. Expect the verdict around 12:10-12:20 UTC. The required actual nnU-Net trainer iteration remains outstanding. Its authored fixture requires Python3.13/A100 and saves a checkpoint; it does not test production loaders or checkpoint reload. Existing Python3.12 pinned image cannot run that unchanged. No GPU reservation or launch; delivery remains held.

Author 1's format-refused draft, original call and charge remain preserved. Repair b84baccd passed233tests and independent APPROVE fc419017/report48b558ca, then installation, native no-call qualification and exact recovery. Author2 corrected the draft through normal accounting; no operator scientific edits or new allowance.

12 October UTC: 44/50 calls: 11 scientific authors, 8 scientific reviewers, 23 administrative implementation reviews and 2 standalone direction attempts. Scientific batch109/128; pnormct3/20. Five of the additional16Colab slots are used, leaving11. Known completed Claude charges$290.76127125; live scientific review charge and author dollars unavailable. Non-Colab item4 exposure$115.516623/$150 = billed$24.487001 plus retained$91.029622. No cap change or new GPU reservation.

Other workstreams: the next fixed-amount smoothing analysis has existing server input references, with all 728 files currently size-matching/readable (metadata-only). Its next result is a reviewed executable specification, one author/reviewer cycle after normal admission; CPU result time is not yet reliable. Meeting preparation has an explicit asset-gap matrix. Its next result is a reviewed synthetic selector/renderer, one author/reviewer cycle after admission; real-panel timing depends on follow-up MRI/clinical provenance and geometry QC. Neither received a new model call while pnormct runs.
