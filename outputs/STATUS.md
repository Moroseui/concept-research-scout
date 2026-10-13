# Research status

- Pnormct's resume failed before training: API and mounted writes created duplicate folders. Its checkpoint remains intact.
- A reviewed mount-only creation fix is delivered for both pnorm arms and L preparation; 54 tests passed, with no scientific changes.
- Pnorm_v2 is operator-reported preprocessing with a live lease; it was not touched. Pnormct remains idle unless Partho resumes it.
- Trash only rechecked-empty duplicates; populated folders and leases stay intact. Multiwin full training still awaits A100 evidence.
- Non-Colab item4: $24.49 billed, $91.03 reserved; known Claude charges $564.81. Colab is unmetered.
- Next result: checkpoint selection and initial pnormct epoch timings, provisionally 15-30 minutes after launch; speedup is unmeasured.
- C: has about 11.3 GiB free, below warning but above the 8 GiB stop. [Instructions and hashes](COLAB_RESUME_20261013.md), [execution plan](13B_EXECUTION_PLAN.md).

Updated 13 October 2026, 22:10 UTC. Action needed from you: optional empty-duplicate cleanup, then corrected pnormct resume. Leave the live pnorm_v2 session alone. Codex/OpenAI remains operator; no Swap point.

## Results and current work

Latest folder repair: pnormct7121a2cc failed before training on duplicate folder names. The operator may trash only rechecked-empty duplicates; keep both populated roots and the live pnorm_v2 session. Sourcec7dac565 passed54 tests and qualified APPROVE31e4ae99/report0b3a1e80. Creation is mount-only with GET-only privacy/uniqueness checks, no folder selection or automatic cleanup. Both pnorm callers and L preparation are patched; multiwin and future full releases must use the reviewed hook. Scientific bytes and gates are unchanged. If an earlier operational file already resumed successfully, let it continue. New filenames/full hashes are in the existing resume instructions. Review cost$3.807831; daily43/50 (7authors,8scientificreviews,26administrative,2direction), science134/140. No running server model call after review; no new compute.

Pnormct is stalled, not complete. Partho reports epochs0-86 completed, a hang at87 and about17.7hours of lease renewal without progress. Returned checkpoint metadata records next_epoch85; its payload has not been opened here. The corrected run will hash-verify before loading. Pnorm_v2 remains operator-reported preprocessing with a live lease; there is no independent live runtime view. Switch after a fresh checkpoint if it is progressing; stop it if stalled.

Operational source2e64b30c received qualified independent APPROVE9012c065/reportbe7f92d1 after31tests. Both exact scientific modules are unchanged. The adapter uses12training/6validation workers on the observed12CPU/167GiB runtime; actual selection follows available CPU/RAM. An external process-group watchdog uses approximately3times recent median epoch time, with bounded startup/phase allowances, logs errors, stops lease-renewing children and requests runtime unassignment on failure. It explicitly migrates only exact expired/unowned old bindings, retaining original records and checkpoint payloads; live owners and mismatches still refuse. No measured performance or bitwise replay claim.

All interactive setup is now in the first120-second cell, including existing Drive/API prompts and notebook capture. The exact ready line appears only on success. Installation and input checks follow; no later authentication or browser capture. L preparation has the same up-front setup without changing its scientific module or preparation-only scope.

Trainer checks need a different boundary because their parent now mounts Drive first. Candidate d3859da8 passed12tests including actual local OS positive/negative isolation controls. Review df553924 gave qualified APPROVE, report 1a8c819d. The updated multiwin trainer check is delivered with SHA256 42cb96dce6f90694ea725bc575bbc596c7144cc19a0b8bb30af4894e6dfccd8b. Actual Colab namespace support remains unmeasured; it fails before pip/GPU if unavailable. Use the new upfront file instead of the older late-prompt check. The pnorm_v2 check template is also corrected, but its accepted PASS needs no rerun.

Multiwin author13's exact preserved correction passed all six actual CPU tests. Its original UNCERTAIN row and charge remain counted. Scientific reviewer12 returned genuine REVISE pending actual A100 evidence; retain that verdict. Packaging source daa78d1d received qualified APPROVE1d7f4f3c/report a5381e48 after 76 tests. The corrected check embeds the unchanged scientific module6cbf8e46 and plans532aa816. No more wrapper work before returned A100 evidence. The prior genuine packaging REVISE rounds and all charges are preserved.

L author3 and scientific reviewer3 are COMPLETE. Five host synthetic groups passed, including three execution-module tests. Reviewer3 returned REVISE: actual A100 trainer/checkpoint/memory evidence and baseline metric comparability remain open. It accepted the scientific fidelity and authenticated baseline binding. No full L training release or A100 memory-fit claim.

The reviewed preparation packager735e0f79 received qualified APPROVE834dc22d/report0a45ce1b after165 tests. It embeds the exact author3 modulec4b76731 and changes only the final CLI selection to the authored --prepare-only route. It preprocesses and creates authentic ResEncL plans, then returns before trainer construction. Its metadata preserves the scientific REVISE and both findings. The delivered file is not a full-training notebook.

Read-only original-source intake found matching Dice and patient-scoring function bodies across six saved Sprint12 notebooks and the L draft. An executed original carries the baseline run identity. The load-cache functions differ, and historical fitting is not independently attested. This evidence is ready for scientific judgment; the operator has not closed the metric finding or recomputed scores.

Meeting author3/reviewer3 are COMPLETE with preparation-only APPROVE and12 isolated tests PASS. The accepted code addresses packed small-U-Net masks, original Sprint13A reconstruction and the combined49 exclusion representation. Remaining real-panel requirements are actual immutable input/admission bindings, qualified source access and independent full-stack image QC. No cases selected or images rendered. Native MRI/transforms are unavailable; CT-space derivatives stay labeled honestly. Recorded outer folds do not establish nested-independent training.

## Deliveries

| Arm | State | Next step |
|---|---|---|
| A1_pnormct | Idle after duplicate-folder refusal; corrected file delivered | Trash only rechecked-empty duplicate, resume verified checkpoint |
| A1_pnorm_v2 | Preprocessing, live lease as last reported | Leave live session alone; no overlapping resume |
| A1_multiwin | Updated early-login trainer check delivered; full training held | Actual A100 check, then scientific review |
| A1_L | Preparation-only notebook delivered; full training held | Return authentic plan receipt, then exact-plan A100 qualification |

- 13B_A1_pnormct_resume_folder_fix.ipynb: SHA256 b8d42af4050ee5b95f12f38fef0eb3d1ef5fdd15fd3a2a1332edbf530b50856d.
- 13B_A1_pnorm_v2_resume_folder_fix.ipynb: SHA256 211d947fb0802fc2c40294e661afc148142c0120b2444dc30b8d57840b0e7032.
- 13B_A1_multiwin_real_trainer_check_upfront_PRIVATE.ipynb: SHA256 42cb96dce6f90694ea725bc575bbc596c7144cc19a0b8bb30af4894e6dfccd8b.
- 13B_A1_L_prepare_folder_fix_PRIVATE.ipynb: SHA256 3be767f7bcf878b00575af40e92e9d22bdc457975262625ad47ff614fd2358d9.

Full files run folds0?4 sequentially for250epochs, preprocess once, resume automatically, skip completed folds and print subprocess errors. Colab is unmetered. Pnormct's earlier trainer PASS remains accepted despite its later evidence-copy failure; never repeat that check solely for preservation.

## Accepted science and held work

Item6 diagnostics, synthesis, Idea2's fixed3?3 interpretation and smoothing are accepted. Sprint14's352 rounded matches share saved fits/cohort; they do not establish independent retraining. Preserve Idea2's large-table inspection limitation. Smoothing ran once in304.77seconds; no useful general small-component rescue was established and fragmentation increased. See [smoothing](SMOOTHING_RESULTS_20261012.md) and [meeting preparation](MEETING_PREPARATION_20261013.md).

Repeats remain parked; coverage-dependent zscore/histeq remain held. Compare new arms against Sprint12 A1 provisionally; small differences need a same-platform repeat.

Timing author24 real CPU integration PASS is retained; reviewer16 failed before reservation on confined ledger access. No GPU timing result. Its old funding scope cannot borrow the remaining purpose-specific calls. The author sandbox and future Claude-operator OpenAI administrative route remain unfinished. No Swap point.

## Spending and daily calls

Non-Colab item4 stage1: **$115.516623/$150**, comprising **$24.487001 billed + $91.029622 reserved**. Timing $5.405445/$25 is included; synthetic CPU $1.118950 awaits billing. Total $1,275, projection $1,200 and item6 $100 stay unchanged. Release excess only for confirmed closed billing; retain open or uncertain reservations. No new provider compute in this continuation.

Known completed Claude charges: **$564.81216925**. Author dollar costs are unavailable. Since the preceding public status, L scientific reviewer3 cost $6.445426 and preparation packaging cost $3.28083475. Earlier genuine approvals, REVISE decisions and mechanical failures remain counted; no usage reset or relabel.

13 October UTC: **43/50**, all current calls reconciled. No model call or server compute is running. Five existing maintenance timers remain waiting; seven historical uncertain records remain preserved with their prior qualifications.

| Type | Count | Purpose |
|---|---:|---|
| Scientific author |7|L drafts1/2/3; meeting drafts1/2/3; multiwin provenance correction13|
| Scientific reviewer |8|Pnorm_v2; L reviews1/2/3; meeting reviews1/2/3; multiwin review12|
| Administrative implementation review |26|Pnorm_v2 harness/packaging; L setup, recovery, continuation, receipt-start and preparation package; meeting setup/amendment; batch140 accounting repairs; multiwin continuation, exact-output recovery and packaging; worker/watchdog review and its qualified successor; trainer upfront isolation review; mount-only folder repair|
| Standalone direction |2|Earlier meeting routing attempt retained; CPU worker/watchdog/resume scope APPROVE|

Scientific batch **134/140**: the six remaining slots are two returned-Colab, two L and two meeting. The explicit12-call approval controls; the later bracketed140/136 message adds no funding.

Administrative reviews used most calls. Batch necessary repairs with direction checks; use existing reviewed packaging and deliver unchanged scientific bytes without repeat review. Defer unrelated components. Latest direction approved the operational worker/watchdog route. Qualified successor review permits the concrete resume and first-cell login packaging; Claude also approved the mounted-parent worker boundary as equivalent for this purpose. No new Colab/GPU PASS is implied. Multiwin's SIMPLIFY instruction remains: no more wrapper expansion before hardware evidence.

## Judgment log highlights

- Preserve recovered author13 and all original charges; no author rerun or scientific verdict relabel.
- Restore only reviewed executable modes after the installer refused; no content or guard change.
- Consult Claude on the service-owned receipt check; install only the independently approved bounded replacement.
- Complete L author3/reviewer3 through normal admission. Do not spend author4 on missing hardware evidence.
- Package the exact authored preparation-only path after165 tests and independent APPROVE; retain both scientific findings.
- Intake original baseline code without executing it; leave scientific metric acceptance to the reviewer.
- Reconcile meeting readiness read-only: the three old interface gaps are addressed, but actual admission and independent QC remain.
- Leave user sessions under operator control; deliver reviewed checkpoint migration rather than restarting folds. No new provider compute or credential changes.
- Preserve failed manifest-read review3dafcfcb and its $4.74497425 charge. Narrow the packet to the entire affected component, retaining full scientific modules and notebooks; no reader or qualification limit changed.
- Combine the operational repair with the new login requirement in one successful review. Use actual OS controls for mounted-parent trainer isolation and obtain Claude review before delivery.

## Backup and exclusions

Last verified public push before this update: 80311392140ba9d21dd7ab96e5001e8ffcecb748. The current update and approved operational projection are queued for a fresh scan and push. Main stays unchanged.

Never publish private evidence, packets, ledgers, streams, private records, patient rows/identifiers, images, masks, weights or caches. Public code is an archival projection, not a standalone deployable release. Returned executed notebooks, meeting3evidence and new multiwin private bindings remain excluded.


Installed projection additionally withholds these flagged/private authority files: docs/COLAB_ACCEPTED_INPUT_REFERENCE_PRIVATE.json, docs/COLAB_ARM_LEVEL_OPERATOR_20261012.txt, docs/COLAB_ARM_ORDER_OPERATOR_20261012.txt, docs/COLAB_AUTHOR5_STATIC_PRIVATE.json, docs/COLAB_BOUND_ADMISSION_PRIVATE.json, docs/COLAB_MULTIWIN_INPUT_REFERENCE_PRIVATE.json, docs/COLAB_MULTIWIN_PRIVATE.json, docs/COLAB_MULTIWIN_RECOVERY_PRIVATE.json, docs/COLAB_REVIEW5_BOUND_PRIVATE.json, docs/COLAB_REVIEW5_OPERATOR_DECISION_20261012.txt, docs/COLAB_REVIEW5_OPERATOR_DISPOSITION.json, docs/COLAB_REVIEW6_DELETE_PRIVATE.json, docs/COLAB_RUNTIME_FAILURES_PRIVATE.json, docs/COLAB_TONIGHT_OPERATOR_20261012.txt, docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt, docs/LIMIT_OPERATOR_DECISION.txt, docs/MULTIWIN_AUTHOR10_TEST_FAILURE_PRIVATE.txt, docs/MULTIWIN_TONIGHT_CONTINUATION_PRIVATE.json, docs/OPERATOR_DIRECTION_20261010.txt, docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt, docs/PNORMCT_REVIEWED_REFERENCE_PRIVATE.py, docs/SCIENTIFIC_BATCH128_OPERATOR_APPROVAL.txt, docs/SCIENTIFIC_BATCH128_OPERATOR_QUESTION.txt, docs/SCIENTIFIC_REVISE_OPERATOR_DECISION_20261012.txt. Exact private copies remain available to the system; public projection is an archive, not self-contained deployment.

Additional exclusions: docs/IDEA2_INTERPRETATION_PRIVATE.json and all review/recovery/diagnosis evidence; orchestrator/cpu_isolation.py and tests/test_cpu_diagnostics_profile.py remain excluded for infrastructure/credential-path findings. No credential contents, paths, endpoints or key names are published.


Also exclude docs/COLAB_L_NATIVE_PRIVATE.json, docs/COLAB_L_QUESTION_PRIVATE.json, docs/L_EVIDENCE_CONTEXT_PRIVATE.json and orchestrator/manual_stage.py, plus private meeting metadata, every review packet, ledger, native stream and notebook. Earlier flagged/private bindings remain excluded from the public projection.

Excluded from this candidate backup: docs/MEETING_PREPARATION_PRIVATE.json (private accounting and native-layout binding). All private evidence, review packets, ledgers and streams remain excluded.

Batch140 exclusions: docs/MEETING_BATCH140_CHECKPOINT_PRIVATE.json, docs/MEETING_BATCH140_EVIDENCE_PRIVATE.md, docs/SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt, docs/SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt, docs/SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json and docs/SCIENTIFIC_BATCH140_PRIVATE.json. All exact private copies are preserved.


Also excluded: exact author13 output/native stream, all L author3/reviewer3 evidence, original executed Sprint12 notebooks, metric-source intake, private plan receipts and delivered notebooks. Public code is an archive, not a standalone deployable release.

Additional exclusions: raw returned pnormct notebooks/checkpoint metadata, exact scientific module/notebook fixtures, all new review packets/streams/receipts, canonical operator records and docs/COLAB_LOADER_STALL_OPERATOR_PRIVATE.txt and docs/COLAB_UPFRONT_OPERATOR_PRIVATE.txt. Public tests refer to private fixtures; the archive is not a standalone deployment.

Publication scanner excludes tools/colab_mounted_drive_worker.py for INFRASTRUCTURE_OR_CREDENTIAL_PATH. Its exact reviewed bytes remain in the private store and delivered private notebooks; no scanner rule was weakened. The public code archive is therefore not self-contained.

Current stop: both repair reviews are genuinely APPROVE and delivered. This continuation used four administrative calls including direction and the disqualified first review, costing $16.22566475 in known Claude charges. No scientific model call or provider compute was added. The two pre-admission packet preparations remain preserved without charge; registered request1d52ba10 was never started and must not be started.

Latest stop: folder review31e4ae99 COMPLETE, qualified APPROVE, $3.807831 counted. No scientific call or provider compute added. Direction was folded into this review; Claude judged it minimal and fail-closed. No separate PROCEED label is inferred. Historical uncertain qualifications stay preserved.

Additional publication exclusions: tools/colab_private_output.py, tests/test_colab_private_output.py and docs/COLAB_PRIVATE_FOLDER_SCOPE.md were flagged EXCLUDED_RECORD_PATH by the unchanged scanner. Exact files stay private; public integration code is an archive, not a standalone deployment. Folder IDs, operator report, review evidence, stream and notebooks stay private.

The updated docs/COLAB_USABILITY.md also received INFRASTRUCTURE_OR_CREDENTIAL_PATH from the publication scanner. Its new version is withheld privately; the prior public version remains. The mandatory folder-release rule is recorded in STATUS, the execution plan and resume instructions. No flagged commit was pushed.
