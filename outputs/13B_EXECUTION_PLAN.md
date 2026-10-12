# 13B execution plan

Updated 12 October 2026,21:24UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Author12 and five synthetic groupsPASS; reviewed recovery installed, scientificreview11RUNNING, then real trainer integration |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Delivered unchanged after real trainer PASS; Partho reports RUNNING |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Author, scientific review and real integration |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Same checks, plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:none. C:14.28GiB clears the disk stop.**13B_A1_pnormct.ipynb is running by operator report. SHA25630bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6. Default Colab A100,Run all,unedited. Built-in estimate14hours/94.78CU. Return completion/error and executed notebook; private Drive outputs are in the notebook's built-in arm folder. The operator-confirmed real trainer PASS is accepted; later cache-copy failure is preserved and no repeat required.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Server work:**Multiwin author12 completed and the lane accepted its notebook and specification. All five synthetic test groups passed, including the formerly failing module fixture. The five-fold notebook hash is2df445002441298d3c17dcc6b43c6a1d5959a275a0b03dc4da184a1b3532aa65; its scientific code remains unchanged by the operator.
Scientific review10 then exhausted its30tool-turn limit without submitting a verdict. Both ledgers record FAILED and its4.4578125charge remains counted. No scientific REVISE or APPROVE is inferred. No modelclient is now live. The exact native terminal proof, all23rows, account/configuration and successful author outputs are preserved. Do not replay review10.
Next: a bounded, independently reviewed recovery for the existing final reviewer11slot, using60tool turns while preserving timeout,tools,permissions,isolation and all call/dollar caps. This repeated mechanical cause requires Claude's second opinion and implementation review together. No new user decision or call allowance is needed. The notebook remains held until scientific approval and its real trainer iteration. Nexttestedreviewrecoverycheckpoint30-60minutes conditional.

Smoothing CPU is valid/terminal; interpretation namespace repair06eb remains deferred/unreviewed. Meeting,timing,sandbox/rotation deferred. No Swap.

Today58calls:14author,10scientificreviewer,32administrative,2direction; installed100on12OctoberUTC then50. Scientific114/128,remaining8Colab/2analysis/4meeting. Completed Claude351.09885125,author dollars unavailable. Item4exposure115.516623/150=billed24.487001+retained91.029622,total1275/projection1200/timing25inside stage1 unchanged. Item6cap100. Colab unmetered.
