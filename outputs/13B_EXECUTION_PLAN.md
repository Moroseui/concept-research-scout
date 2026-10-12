# 13B execution plan

Updated 12 October 2026, 23:56 UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Author12 and five synthetic groupsPASS; Synthetic-only package APPROVE/delivered; Partho runs freshA100check; fulltrainingheld until returned evidence is scientifically accepted |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Delivered unchanged after real trainer PASS; Partho reports RUNNING |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Author1 complete; reviewer1 exhausted tool turns without verdict; recovery under review; synthetic failure preserved; real trainer evidence still required |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Same checks, plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:** run/return the delivered multiwin synthetic trainer check in a fresh A100 session; leave pnormct running. Pnormct's unedited all-fold notebook is already delivered and running, SHA25630bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6. Built-in estimate14hours/94.78CU. Return completion/error and executed notebook; private Drive outputs use the built-in arm folder.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Parallel server work:** Pnorm_v2 author1 completed. Four synthetic groups passed and coverage handling failed. Reviewer1 exhausted its30 tool turns without a verdict; the recovery patch is under independent implementation/direction review. Scientific verdict provisionally20-40minutes after23:56UTC if approved. Item6, Idea2 and smoothing interpretations are accepted; no new saved-results execution is running. The [meeting reading sheet](MEETING_READING_SHEET.md) is ready; private panels await source provenance and reviewed rendering. No panel ETA is reliable yet.

**Timing diagnostic:** current-resource RunA versus increased-CPU/augmentation-worker RunB remains approved within its $25 sub-cap. RunB first if both will not fit. Author24's real CPU integration passed; reviewer16 failed before reservation on confined ledger access. The established reader can be reused, but old timing allocation rules also predate the current119-call history. Reconcile retained timing authority with the later purpose-specific batch allocation before preparing a complete narrow repair; no existing allowance is silently repurposed. No GPU job is running, and Colab arms do not wait for this repair. Timing ETA follows repair approval; no measured steady-state projection is claimed.

**Money and limits:** Item4 non-Colab stage1 $115.516623/$150: $24.487001 billed plus $91.029622 retained reservations. Timing exposure $5.405445/$25 is included. Total $1,275 and full-training projection gate $1,200 unchanged. Colab is unmetered by operator decision; printed units are estimates only. 12October model usage70/100, daily cap50tomorrow; scientific batch119/128 leaves5Colab and4meeting calls, no analysis allocation. Detailed audit and costs: [STATUS](STATUS.md).

-23:38UTC: pnorm_v2 author output hashes verified; synthetic failure retained; scientific reviewer1 admitted normally. No administrative call or provider compute added this turn.
