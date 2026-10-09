# Research status

Item 6 is complete; all 352 comparable values match the independent Colab run.
A100, H100 and B200 benchmarks are complete: first epochs took 278.17, 228.14 and 166.28 seconds; the fixed rule selects B200.
The two smoke runs are prepared; no GPU smoke is running yet.
Claude is reviewing the deliberate interruption/resume control; coverage-dependent arms and full training remain held.
Identified provider compute is $13.97; later billing is pending. Last verified exposure was $81.74, before the new $1 setup reservation, within $150.
Next expected result: five-epoch smoke with real interruption/resume and repeat, about 1-2 hours if this review approves.
Today: 50/50 model calls. Latest direction: PROCEED. Further model calls wait for the UTC reset.

Updated 2026-10-09T22:50:01.781893+00:00.

## Results and readiness

All three benchmark outputs are collected, hash-verified and positively terminated. B200 completed 250 training and 50 validation iterations in 166.28362007700002 seconds; loader wait was 0.692260330000039 seconds and all seven validation checks passed. The unchanged hardware calculation selects B200. These are first-epoch measurements, not steady-state smoke results or scientific acceptance of full training. Safe aggregate outputs are under outputs/sprint13b/.

The installed smoke connection is source aa833acb4980520f67256f43fe13a20a818b4d03, independently approved by report 8d1b54f44b373ed169f172ee7eb697ed7f8162eaccafa707af61c76e5276fef8. Both new smoke identities are now READY under a normal $1 setup reservation, with the same image, frozen inputs, preprocessing and shared package. Runtime publication and execution preparation completed; no setup action was duplicated. Root wave publication and GPU launch await the next approval.

Candidate 2e6bfd6a66610e775ad8c4b64fcd75ec3cbd437f connects the existing checkpoint, termination and continuation APIs for the first base smoke. It stops only after an authenticated partial checkpoint, records an exclusive stop intent, refuses uncertain repeat termination and verifies the full terminal checkpoint before ordinary accounting and resume. It adds no timer or subsystem. 187 tests passed with two skips; 40 focused tests passed after a runtime loader typo was caught and corrected. Exact final cold connection, native unit parsing and read-only replay of the actual two-fit publisher passed. Only future candidate approval was simulated; no scientific result or approval was fabricated. One combined independent implementation/accounting/safeguard review is running. Uninstalled code is preserved on the working branch only.

## Timing and provisional full-plan cost

A100 first-epoch timing includes unseparated in-epoch warm-up and excludes initialization before the epoch timer. Sprint 12 A1 had measured epoch medians of 36 seconds across its five folds; fold training durations were 2.69, 2.69, 2.72, 2.74 and 2.72 hours. Naively extending the A100 first epoch over 40 fits of 250 epochs gives 772.686 epoch GPU-hours plus 40 fixed hours, or 812.686 hours total. GPU-only cost is about $1,931.72; the current full resource and fixed-allowance calculation is about $6,573.41, above the $1,200 gate. This is a provisional diagnostic extrapolation, not an accepted full-training projection. Steady-state smoke measurements and author/reviewer judgment remain required.

## Money and model calls

Stage-one cap $150, full-training projection gate $1,200 and total cap $1,275 are unchanged. Last verified closed-benchmark effective exposure was $81.742729, before the new $1 setup reservation; this is conservative accounting exposure, not an invoice. Original compute reservations totaling $97.9392 remain preserved. B200 retains its original $16.5924 reservation alongside a closed-attempt conservative bound of $10.039474, including unsettled obligations. Identified provider compute is $13.96614730, including H100 $2.07549804; B200 final billing, assets and model charges are not included in that partial compute total. No open or uncertain reservation is released.

Daily calls: 3 scientific authors (native corrections 12/13 and staging 14); 4 scientific reviewers (7, reader-failed 8, 9 and 10); 37 administrative reviews (implementation, accounting and process repairs, including the current deliberate-stop bundle); 6 standalone direction checks (retry authority and next-result planning). Administrative reviews dominate; required controller, accounting and publisher changes are bundled into this single call, with no extra direction call. At 50, wait for UTC reset without resetting or relabeling usage.

## Judgment log and blockers

Latest direction at 22:13 UTC: PROCEED with the original B200 then approved smoke; defer unrelated infrastructure, accounting refinements and new watchers. The benchmark finished. Judgment: prepare already-approved smoke assets and runtime records while implementing only the missing deliberate-stop connection; consult Claude in its required implementation review because it touches termination safeguards and accounting. Preserve every original attempt and charge. Earlier assumptions that the stall monitor supplied deliberate interruption were corrected by source inspection before launch. The runtime-wiring typo was caught during final native rehearsal, corrected before review, and its original commit and failure retained.

Immediate blocker: genuine implementation APPROVE before installation and base smoke. Full training separately requires scientifically accepted smoke results and a projection within its gate. No money decision is pending. No main merge, BACKLOG edit, credential change, patient restriction change or safeguard relaxation. Public source projections omit private dependencies and are not deployable combined releases.

## Files withheld from public backup

- configs > pilot > colab-worker-future.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > DIAGNOSTICS_OPERATOR_DECISION.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_FRESH_RUNTIME.json: CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_FRESH_START_CHECKPOINT.json: CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_PINNED_IMAGE_SELECTION_20261008.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_PREPROCESSING_FRESH_SCOPE.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW5_CONTINUATION_PLAN_20261008.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW6_CONTINUATION_PLAN_20261008.txt ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVIEW8_DELIVERY_SCOPE_20261009.txt: INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVISION_EVIDENCE.json ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- docs > ITEM4_REVISION_EVIDENCE.json: INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_ACCOUNTING_OR_EVIDENCE_RECORD
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
- docs/ITEM4_BENCHMARK_HANDOFF.md: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json: CREDENTIAL_OR_HOST_REFERENCE, EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_PRIVATE_STAGING_SCOPE.txt ? CREDENTIAL_OR_HOST_REFERENCE, EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- docs/ITEM4_STAGING_RETRY_CHECKPOINT.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- docs/ITEM4_STAGING_RUNTIME.json ? CREDENTIAL_OR_HOST_REFERENCE, INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- orchestrator > colab_worker.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > cpu_isolation.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > experiment_provisioning.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > inspection_access.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
- orchestrator > inspection_runtime.py ? INFRASTRUCTURE_OR_CREDENTIAL_PATH
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

Earlier detailed checkpoints and accepted reports remain in branch history and outputs/. Current status is maintained here in place.
