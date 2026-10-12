# 13B execution plan

Updated 12 October 2026,18:59UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Bounded continuation153testsPASS; independent implementation review held by disk8GiBstop; then correction,scientific review,integration |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Delivered unchanged after real trainer PASS; Partho reports RUNNING |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Author, scientific review and real integration |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Same checks, plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:free at least2GB on C:; disk7.78GiB is below8GiBstop.**13B_A1_pnormct.ipynb is running by operator report. SHA25630bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6. Default Colab A100,Run all,unedited. Built-in estimate14hours/94.78CU. Return completion/error and executed notebook; private Drive outputs are in the notebook's built-in arm folder. The operator-confirmed real trainer PASS is accepted; later cache-copy failure is preserved and no repeat required.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Server work:**priority is multiwin delivery,provisionally1-2hours after diskclearance if correction/review/integration pass. Cap099b76cd is APPROVED/installed; process/cache questions were not answered. Candidatebb65a300passes153tests and needs one independentimplementationreview before use. No continuation installed yet. Smoothing CPU execution is valid and terminal; its interpretation repair06eb remains deferred and unreviewed. Meeting,timing and generic sandbox/rotation work are deferred.

Today51calls; operator authorizes100for12OctoberUTC then50. Cap implementation is installed and verified; no servercallrunning. Scientific111/128,remaining11Colab/2analysis/4meeting. Item4non-Colab exposure115.516623/150=billed24.487001+retained91.029622;total1275/projection1200/timing25inside stage1 unchanged. Item6cap100. Colab unmetered.
