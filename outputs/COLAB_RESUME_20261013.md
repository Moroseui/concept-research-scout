# Colab: resume with workers, stall protection and all logins first

Use these corrected files from Downloads, unedited, in a fresh default Colab A100 high-RAM runtime. For a running arm, wait for its next checkpoint if it is progressing; then Disconnect and delete its old runtime. Allow five minutes for the old lease to expire. Never run old and corrected notebooks for the same arm concurrently and never edit a lock.

Click Run all and complete the first-cell Drive and API prompts. Wait for **All logins done, you can leave now**. All browser-dependent notebook capture also happens there, before installation. Google may require both existing login flows; none is deferred. If first-cell setup fails, no installation or training starts and the ready message is not printed.

| File | SHA256 |
|---|---|
| 13B_A1_pnormct_resume_workers.ipynb | 7121a2cca22fa2f71bec9ba97811d07e9b3dc6ae7dd3e2ec76ed1db11a9763d1 |
| 13B_A1_pnorm_v2_resume_workers.ipynb | e8b709f98cade842444b06895d44aad892414915486c344fd5980438c27c4809 |
| 13B_A1_L_prepare_upfront_PRIVATE.ipynb | e5f4770b544c496d22494534d2453d7ec6368e6624b6832da4c98eb7b119dd77 |


Pnormct should resume at epoch85 from the reported checkpoint, after actual payload-hash and binding verification; it need not restart fold0. Epochs85-86 may be repeated. Pnorm_v2 resumes its own latest valid checkpoint. Both retain the same private output folders, inputs, scientific code,250epochs, folds0-4 and scoring. Completed folds remain verified/skipped. L's file remains preparation-only, with no trainer construction or full training authorization.

Workers are selected from observed CPU and RAM; the returned12CPU/167GiB profile gives12training and6validation workers. This is not a measured speedup. At the old190-196seconds/epoch rate, five folds take roughly67-68hours before extra overhead, not14hours. Existing repeated input hashing remains unchanged. Return the first few completed epoch timings and worker count privately.

During training, stalls are bounded to roughly3times the recent median completed-epoch time, with2-30minute bounds and15minutes for the first resumed/compiled epoch. Other phases have30minute bounds. The watchdog kills the training process group, prints the last logs, attempts a private failure record and requests Colab runtime unassignment. Deallocation is not guaranteed if Google refuses; the notebook prints a Disconnect/delete fallback. No automatic retry.

Independent implementation APPROVE: source2e64b30c, review9012c065, reportbe7f92d1;31testsPASS including real subprocess and exact scientific lease/checkpoint tests with synthetic files. No new A100 performance qualification or scientific conclusion is claimed. Full review/hash details remain private.
