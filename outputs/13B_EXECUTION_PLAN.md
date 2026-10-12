# 13B execution plan

Updated 12 October 2026,14:20UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Parked at20calls after fixture and mechanical-review failures; scientific correction, approval and real integration remain |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Scientific code APPROVE; private trainer check sent, full training notebook held until verified PASS |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Author, scientific review and real integration |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Same checks, plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:** the separate synthetic-only integration check, **13B_A1_pnormct_real_trainer_check_PRIVATE.ipynb**, is in Downloads. SHA256:8513ad04b3891d9871336844086d9a7b28a106d95303dc1fa70408d02ffc01f3. Open one fresh default Python3.13/A100 runtime and Run all, without edits. Allow10-25minutes (informational1.13-2.82CU). It uses exact scientifically approved code/plans; Drive mounts only after execution ends to preserve evidence. Return printed PASS/FAIL and the private evidence-folder location; keep the runtime open until saving succeeds. It tests trainer construction, one update and checkpoint save, not production loading or checkpoint reload. No result is yet confirmed. This is not the full training notebook.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Parallel server work:** the smoothing CPU analysis completed successfully once on99development patients, with728input/4package before-after hashes unchanged and no incremental provider cost. Interpretation preparation hit a namespace collision; repair06eb2957passes136tests and awaits independent review after the daily reset. Original outputs and failed preparation are preserved; no rerun. Next reviewed interpretation is provisionally45-90minutes after00:00UTC13October, subject to repair approval. Meeting selection remains fixed but real panels await provenance/geometry checks. Timing and generic sandbox/rotation work stay deferred.

Today50/50model calls; scientific111/128. Remaining allocation:11Colab,2analysis,4meeting. No new call before UTC reset and normal admission. Item4 non-Colab stage1exposure115.516623/150 (billed24.487001,retained91.029622); total1275/projection1200/timing25inside stage1 unchanged. Item6cap100. Colab unmetered. Latest Claude direction13:56UTC:PROCEED, caution to simplify future reused-component installation overhead; agreed.
