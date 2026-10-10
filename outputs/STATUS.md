# Research status

Item 6 is complete: all 352 comparable values match the independent Colab run.

13B CPU starvation is still unanswered; two synthetic fixture failures stopped the path to GPU measurement.

Author21 is accepted. All 16 controller tests pass, including the new callback regression test. The reviewed connector is installed. One CPU validation is confirmed RUNNING on the provider, with a $1.118950 reservation.

Claude approved the native-validation and accounting bundle with no findings and recommends PROCEED; root agrees.

Identified compute cost is $24.33873. Both failed CPU attempts cost $0.04859; their original reservation records remain preserved. After a $0.189305 compute-only credit and the new reservation, commitments are $113.278723/$150, including $3.167545/$25 for the diagnostic.

Next expected result: native CPU validation within about 20 minutes of the14:15 UTC service start. GPU timing follows only after native success and scientific review.

Run B remains first. Full training, coverage-dependent arms and the $1,200 projection gate remain held.

Today's calls: 38/50: 7 authors, 5 scientific reviews, 20 implementation reviews and 6 direction checks. All model calls are terminal; no new scientific call has started.

## Current work and evidence

Live check at14:18 UTC: the same approved service is running one reserved native CPU operation on the provider. The complete payload was sent once. The live accounting event confirms the $1.118950 reservation and the bounded $0.189305 credit; both original failed rows remain byte-equivalent. Installation completed with both runtime checks passing and zero model/provider calls. Do not duplicate the service. Its single CPU operation has a900-second provider hard stop and no automatic retry.

[Independent implementation APPROVE](reports/item4-audited-native-verification-20261010.json), report4fba65d3, covers exact sourceea529258, one deliberately reviewed CPU operation and actual-PASS-gated reviewer16. The review also approved compute-only billing reconciliation with original rows retained and two overhead allowances still held. All165 focused tests and the final4-test role-order recheck pass. Current-source server rehearsals verified the original history, normal native reservation, over-cap refusal after credit, and one counted review16 only with a test-only simulated future PASS in a disposable copy. No live ledger changed in rehearsals. Scientific review15 and all global findings remain open. The [author-owned module](proposals/item4-cpu-diagnostic-author21.py) is an exact scan-passing copy of accepted21; it is not scientific approval or GPU evidence.

The latest genuine direction report e9636a72 is REVISE because the scientific defect remains, with PROCEED/SIMPLIFY advice for a whole-fixture repair. It is not installation approval. The earlier constructor error was followed by a missing telemetry callback in the corrected fixture. Both native operations are positively terminal failures; complete originals remain private. Neither used patients or a GPU. No automatic retry is scheduled.

Approved source 28a6e1a5 permits one author21 response to genuine scientific review15. Only the synthetic fixture body and appended contract tests may change. Production code, interfaces, existing tests, scientific choices, plan and image remain fixed. Both failure records and all seven scientific findings reach the author. Acceptance ends with execution and reviewer16 held. [Independent implementation APPROVE](reports/item4-whole-fixture-author-20261010.json), report931c7a1a, covers this exact scope. Installation, held runtime verification and zero-call activation passed. Author21 was admitted once through normal accounting and completed. The author repaired the whole synthetic fixture and demonstrated the retained callback failure; the controller accepted the result. This is synthetic evidence, not native or GPU evidence. No duplicate call or watcher was started.

The real server rehearsal passed using read-only live records and disposable ledger copies. It admitted exactly one counted author call with the proposed bounded 39/77 allowance, preserved all original events, and refused duplicate, reviewer16 and full-plan calls. The simulated future approval was test-only. No live ledger changed. There are 84 passing current focused checks. The first broad regression had 266 passes; its 15 outdated handoff-test errors/failures subsequently passed after fixture updates. Four legacy compute-budget tests still fail identically on the installed baseline and candidate, in unchanged source; they are disclosed and deferred, not labelled passes. Claude explicitly found they do not block this non-compute release. The final real-server rehearsal also refused the 51st daily call, changed original rows/reservations, missing authority and pending work. The first failed rehearsal and all initial test failures remain preserved.

Scientific review15 remains a genuine REVISE: corrected instrumentation needs native integration evidence before paid A/B diagnostics. Global provenance, coverage, remaining arms, projection and opposing-review findings remain unresolved. No administrative approval closes them.

## Spending and call purposes

- Stage1: conservative counted commitments $113.278723 of $150; diagnostic actuals plus retained/open allowances $3.167545 of $25.
- First native attempt: provider actual $0.02512208, original reservation $1.118950 preserved; excess CPU/RAM credit $0.093827 recorded. Second: actual $0.02347152, original $1.118950 preserved; excess credit $0.095478. Each retains $1 overhead whose obligations are not yet settled. The current third attempt has a full open $1.118950 reservation and unknown actual cost. Nothing from the running attempt has been released.
- Identified compute total $24.33872805 includes the newly confirmed second attempt and is separate from model costs. Every older usage row is unchanged; the newly billed rows belong only to this second attempt. The latest administrative review estimated $5.782551, separately retained and counted.
- Full-plan projection gate $1,200 and total cap $1,275 are unchanged. No new GPU diagnostic reservation has been made.
- Seven author calls: smoke response, timing proposal, interface correction, native fixture, plaintext correction, fixture correction and the current whole-fixture audit.
- Five scientific reviews: smoke, timing response, diagnostic design, scoped native evidence and fixture correction.
- Twenty implementation reviews: bounded author/reviewer handoffs, native connector, installation and accounting repairs; most recently the current native-validation and bounded billing bundle.
- Six direction checks: scope and recovery decisions, most recently the second native fixture failure. Related engineering checks were bundled into the approved implementation review; no optional component or separate direction call is planned.

## Judgment highlights

Latest Claude check: the mandatory implementation review also gave PROCEED, one round agreement, with no findings. Audit the whole fixture, add a fast counterexample test, reuse existing routes, and defer optional infrastructure. Preserve the formal REVISE and both failed reservations.

Root's engineering judgment: the author-only successor needs exact historical accounting bindings, not a general duplicate-review exception. It requires a new genuine review15 response and refuses later calls. Claude independently approved the concrete scope and exact equivalent historical checks. The installed runtime verification passed and the one approved author call completed. Root has made no scientific repair. The independently approved connector now binds exact accepted21 bytes, retains both failures and the existing39/77 call allowance, and admits reviewer16 only after genuine native PASS. GPU dispatch remains outside that scope.

The status file has been consolidated in place to remove contradictory historical checkpoints. Earlier versions remain in Git history; private originals and judgment logs are retained.

## Backup and exclusions

Installed code is on `remote-server`, including the reviewed whole-fixture handoff. Safe projection f03283ac from `astra/public-whole-fixture-author-20261010` is merged as the installed release and contains byte-exact scan-passing source and tests. Private frozen documents are excluded, so this public projection is not independently deployable. Raw working history is withheld because it contains forbidden records. Main is unchanged.

Installed audited-native sourceea529258 is backed up through safe projectionae85e8bb from `astra/public-audited-native-verification-20261010`, now merged into `remote-server`. Its four private contracts remain withheld. Normal admission recorded the approved $0.189305 excess CPU/RAM credit, retaining $2 overhead, and reserved $1.118950 for the current CPU run. Original rows, statuses and full reservation figures remain unchanged; append-only records explain effective costs.

Before each push, every new reachable blob and commit message is scanned for privacy, secrets and infrastructure details. Evidence, ledgers, review packets, native streams, private files and patient-level data remain excluded. Flagged files retained privately include:

- configs > pilot > colab-worker-future.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > DIAGNOSTICS_OPERATOR_DECISION.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_FRESH_RUNTIME.json: CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_FRESH_START_CHECKPOINT.json: CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_HOST_PROOF_PREFLIGHT_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs > ITEM4_PINNED_IMAGE_SELECTION_20261008.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_PREPROCESSING_FRESH_SCOPE.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW5_CONTINUATION_PLAN_20261008.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW6_CONTINUATION_PLAN_20261008.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW8_DELIVERY_SCOPE_20261009.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVISION_EVIDENCE.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVISION_EVIDENCE.json: INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_ACCOUNTING_OR_EVIDENCE_RECORD
- docs > ITEM4_SMOKE_REVIEW_CHECKPOINT_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs > ITEM4_VALIDATION_ADMISSION_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH; withheld.
- docs > M3_HOST_PROOF_TRANSITION.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > M3_INTERPRETATION_EVIDENCE.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > M4_PRIVATE_SCIENTIFIC_INTAKE.md ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- docs > MANUAL_LOGIN.md ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > RC4_PORTABILITY_SWEEP.md ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > REVIEW_PACKET_POLICY.md ? PRIVATE_RECORD_PATH
- docs > STEP_C_REVIEW.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > STEP_D_ISOLATION.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > STOCKTAKE_REVIEW_CONTINUATION.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > BRANCH_AND_AUTHORSHIP_20260906.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > CLAUDE_EXECUTION_WORKER.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > CLAUDE_WORKER_INTEGRATION_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > CLEANUP_RECONCILIATION_20260906.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > CLEANUP_REVIEW.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > COLAB_MCP.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > COLAB_MCP_CONNECTED_TEST_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > COLAB_MCP_TEST_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > COLAB_MCP_WINDOWS_HELPER_TEST_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > COLAB_MCP_WSL_TEST_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > MAIN_INTEGRATION_VERIFIED_20260906.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > P001_DISPATCH_BLOCKED_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > P001_DOWNLOAD_SYSTEM_BATCH_20260905.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > PRIVATE_COORDINATOR_PLAN.md ? PRIVATE_RECORD_PATH
- docs > isles-pilot > PRIVATE_COORDINATOR_SETUP.fish ? PRIVATE_RECORD_PATH
- docs > isles-pilot > PROGRESS.md ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > reviews > human-controls-final-r1.response.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > isles-pilot > reviews > human-controls-final.response.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > CONTINUING_RESEARCH_AUTHORIZATION_20260911.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > CONTINUING_RESEARCH_POLICY_20260911.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > CURRENT_MILESTONE_20260908.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > DEPLOYMENT_BUNDLE_PREPARATION.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > GOOGLE_OAUTH_OPERATOR_WINDOW_20260908.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > HOSTED_ACCEPTANCE_20260906.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > HOSTED_CYCLE_IMPLEMENTATION_REVIEWS_20260906.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > OPERATOR_WINDOW_READY_20260908.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > RESTART_HANDOFF_20260909.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > daily > 30890a0470b97064428ba9d7dc09da95f1b46b4bfe65349311bc9b0222942b89.astra-disposition.md ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 50-handover-a0795e6-continuation.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 50-handover-a0795e6-disposition.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 50-handover-a0795e6-review.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 51-handover-a0795e6-continuation.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 51-handover-a0795e6-disposition.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operations > hosted-completion-20260907 > 51-handover-a0795e6-review.operating-context.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operator-decisions > 20260927-m4-successor-contract.binding.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > operator-decisions > 20260928-copy-recovery.binding.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > science > 047B_PRIVATE_ACCEPTANCE_APPROVED_20260908.json ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- docs > science > 047B_PRIVATE_ACCEPTANCE_PACKET_20260908.json ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- docs > science > 047B_PRIVATE_ACCEPTANCE_PACKET_20260908.md ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- docs > science > P001_TRANSPARENT_NATIVE_SOURCE_REVIEW_20260908.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs/ITEM4_AUTHOR20_NATIVE_REFERENCE_PRIVATE.py: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_BENCHMARK_HANDOFF.md: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json: CREDENTIAL_OR_HOST_REFERENCE, EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json (EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH).
- docs/ITEM4_DIAGNOSTIC_NATIVE_ACCEPTED_PRIVATE.json (EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH).
- docs/ITEM4_DIAGNOSTIC_NATIVE_SELECTION_PRIVATE.json (EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH).
- docs/ITEM4_DIAGNOSTIC_REVIEW_PRIOR_UNIT_PRIVATE.txt (EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH).
- docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_PRIVATE_STAGING_SCOPE.txt ? CREDENTIAL_OR_HOST_REFERENCE, EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_RESPONSE_HOST_PRIVATE.json (EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH).
- docs/ITEM4_RESPONSE_HOST_PRIVATE.json: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_RESPONSE_HOST_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_STAGING_RETRY_CHECKPOINT.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- docs/ITEM4_STAGING_RUNTIME.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- docs/ITEM4_WHOLE_FIXTURE_AUTHOR_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- orchestrator > colab_worker.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > cpu_isolation.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > experiment_provisioning.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > inspection_access.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > inspection_runtime.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > item4_smoke_review.py: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- orchestrator > ledger.py ? PRIVATE_RECORD_PATH
- orchestrator > manual_auth.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > manual_isolation.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > manual_runtime.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > manual_stage.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > notebook_synthetic.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > p001_native_setup.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > private_records.py ? PRIVATE_RECORD_PATH, PUBLICATION_TYPE_REJECTED
- orchestrator/item4_private_staging_retry.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- outputs > proposals > item4-preprocessing-root-repair-20261009.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- outputs > sprint13b > REVIEW8_DELIVERY_PROPOSAL.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- outputs/implementation-reviews/item4-private-package-staging-20261009.json: PRIVATE_RECORD_PATH; original accepted report remains private, decision and hash are recorded above.
- tests > fixtures > context_budget > round2 > PROVENANCE.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > context_budget > sprint10 > PROVENANCE.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > item4_cost_bootstrap_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > item4_deliberate_smoke_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests > fixtures > item4_execution_billing_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > item4_fresh_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > item4_pre_science_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > fixtures > item4_smoke_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests > fixtures > item4_smoke_retention_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests > fixtures > item4_smoke_review_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests > fixtures > item4_stage1_cap_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests > test_autonomy_m1.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_autonomy_review.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_direct_storage_service.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_environment_inventory_service.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_experiment_authoring_promotion.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_experiment_preprocessing_dispatch.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_experiment_preprocessing_dispatch.py: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_experiment_waves.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_inspection_access.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_inspection_canary.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_inspection_runner_offline.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_inspection_runtime.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_item4_image_runtime.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_item6_input_preparation.py ? CASE_LEVEL_RECORD_REJECTED, CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_ledger_object_group.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_live_handover_install.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_live_research_preparation.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_manual_isolation.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_manual_promotion.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_manual_rc2.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_manual_rc3.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_manual_release.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_mcp_review_pipeline.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_modal_diagnostics_image.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_modal_direct_storage.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_modal_environment_provider.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_modal_mount_recovery.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_modal_runtime_schema.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_p001_native_launch.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests > test_private_git.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- tests > test_private_records.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH
- tests > test_reviewed_deployment_install.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tests/fixtures/item4_benchmark_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests/fixtures/item4_checkpoint_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- tests/fixtures/item4_closed_billing_prior_unit.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- tests/fixtures/item4_smoke_response_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- tests/fixtures/item4_staging_prior_unit.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- tests/test_experiment_preprocessing_dispatch.py: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- tests/test_private_preprocessing_package.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- tools > autonomy_review_host.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > deploy_autonomy_review.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > environment_inventory_service.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > install_item4_validation.py: INFRASTRUCTURE_OR_CREDENTIAL_PATH; withheld.
- tools > install_m3_post_smoke_host.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > install_modal_provider.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > install_modal_transition.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > item6_input_preparation.py ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > manual_promotion.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools > private_checkout.py ? PRIVATE_RECORD_PATH, PUBLICATION_TYPE_REJECTED
- tools > recover_item4_provenance_20261008.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- tools/install_item4_private_staging.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- tools/item4_private_staging_runtime.py ? EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.

- docs > ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH; audited-native draft withheld.

- docs > ITEM4_DIAGNOSTIC_NATIVE_ACCEPTED_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH; audited-native draft withheld.

- docs > ITEM4_DIAGNOSTIC_NATIVE_SELECTION_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH; audited-native draft withheld.

- docs > ITEM4_RESPONSE_HOST_PRIVATE.json: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH; audited-native draft withheld.
