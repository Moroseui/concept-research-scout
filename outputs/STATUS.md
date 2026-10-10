# Research status

Item 6 is complete; all 352 comparable values match the independent Colab run.
All three benchmarks, the five-epoch base smoke with real interruption/resume, and the repeat are collected, hash-verified and terminated. No GPU is running.
The repeat's post-first-epoch times average 90.41 seconds and are still declining; stable steady-state timing and scientific acceptance remain unestablished.
Provisional repeat-based full-plan cost is about $3,575 over 291.1 GPU-hours with existing allowances, above the unchanged $1,200 gate.
Identified provider compute is $24.29; current effective stage-1 exposure is $110.11/$150, retaining original reservations and unsettled overhead.
The connection passed 137 tests, cold rehearsal and independent implementation review; it is installed and activated. The server is preparing the single scientific review, expected within 30-60 minutes.
UTC October 10 calls: 3/50: one implementation review and two rounds of one direction discussion. Latest Claude outcome: PROCEED/agreement; full training and coverage arms stay held.

Updated 2026-10-10T01:23:28.528152+00:00.

## Results and readiness

Item 6 is independently accepted, and all 352 comparable aggregate values match the separate Sprint 14 Colab run. Its published aggregates and comparison remain unchanged.

The A100, H100 and B200 benchmarks are collected and verified. Their first-epoch times were 278.17, 228.14 and 166.28 seconds, respectively. B200 remains the selected device under the existing rule. The A100 measurement includes first-epoch warm-up within the timer, excluding preparation before the timer.

The base smoke was deliberately terminated after its first native epoch. Its original checkpoint was loaded at native epoch 1 by the continuation, which returned all five epochs and passed all seven declared checks. The repeat returned all five epochs, started without a loaded checkpoint, and passed all of its declared checks. Original returned file hashes, native collection receipts, local/global records and positive provider termination were checked. These are execution-validation results, not independent scientific acceptance or evidence of full-training efficacy.

The base returned synchronized epoch timings were 173.37, 178.47, 73.44, 73.45 and 67.41 seconds. The first two correspond to separate process starts around the deliberate interruption. The base's last three average 71.43 seconds. Repeat timing originals and separate provisional arithmetic are under outputs/sprint13b/repeat-smoke and SMOKE_REPEAT_TIMING_COMPARISON.json. The repeat post-first-epoch sequence is 103.62, 93.73, 86.50 and 77.78 seconds; its mean is not an established steady-state estimate. Warm-up filtering and extrapolation remain for the scientific reviewer to judge. Native rounded live-log times cover a narrower interval than returned synchronized epoch measurements; they are not substituted for the returned originals.

Sprint 12 A1 reported a rounded median of 36 seconds per epoch. Identical workload and timing boundaries have not been established. At 90.41 seconds per epoch, provisional arithmetic for 40 full fits of 250 epochs gives 251.1 training GPU-hours, plus 40 fixed hours. With the unchanged resource rate and $200 fixed allowance the projection is $3,574.95; it exceeds the $1,200 gate. This arithmetic has not changed installed projections or admitted full training.

## Spending and calls

The stage-1 cap is $150; the full-training projection gate is $1,200 and item total cap is $1,275. The cap change passed independent implementation review and over-cap refusals before installation.

Identified provider compute is $24.29013445, including the repeat at $4.65640856 and both base segments together at $3.66466686. This is identified provider compute, separate from asset costs, model estimates and final invoices. No fabricated per-segment allocation is made for the provider's combined base bill.

Current effective stage-1 exposure is $110.111178/$150 after the installed reconciliation policy applied completed-hour repeat billing. Original compute reservations total $147.7164 and remain preserved. The repeat keeps its original $16.5924 reservation alongside provider compute of $4.65640856 and a conservative closed bound of $9.707803. The $6.884597 excess is no longer included in effective exposure; unsettled overhead is retained. Both base segment originals and their closed bounds remain. No manual credit, ledger rewrite or release for an open or uncertain attempt occurred. The aggregate billing record is under outputs/sprint13b/STAGE1_SMOKE_BILLING.json.

UTC October 10: 0 scientific author, 0 scientific reviewer, 1 implementation review, 2 direction calls. Their purposes were the shortest smoke-review path and clarification of its exact call-accounting exception. Both are completed administrative calls, with model estimates $2.7915255 and $2.13659325. The implementation review is also complete, with a model estimate of $4.94008025; the scientific call has been requested but was not yet admitted at the latest observation. October 9 remains 50 calls: 3 scientific author, 4 scientific reviewer, 37 administrative implementation reviews and 6 direction checks. No usage was reset or relabeled. The completed implementation review bundled the complete smoke connection, accounting, evidence delivery and installation. No extra standalone direction call was made.

## Blockers and judgment calls

Claude and root reached agreement after two rounds at 00:18 UTC: use one ordinary scientific run_spec_review11 for the real five-fit evidence, omit an extra author interpretation call, and preserve the final whole-plan interpretation pair. Development scope is item27/batch65 with all previous calls and charges preserved. The direction agreement authorized development only; the subsequent genuine implementation APPROVE and connected checks now permit the installed one-use review connection. The scientific reviewer will receive the unchanged author's criteria/code/plan, original REVISE10 and actual benchmark/smoke/resume evidence.

The original repeat was observed COMPLETE, collected once, then verified against returned file hashes and native/local/global receipts with positive termination. Judgment: reuse the installed control and read-only inspection/export tools; no installed repair, extra launch, new watcher or model call was needed. Claude was not consulted again for these already-approved operations. A private read-only snapshot preserves the five-fit checkpoint and every original call hash for the scoped connection.

No main merge, BACKLOG edit, credential change, patient restriction change or safeguard relaxation occurred. Full training and coverage-dependent arms remain held. No money decision is pending. The installed review connection is source 7a8f4d662a2a3f8bb2b7032f0e7bfd3d620c7671, approved by report fb04e156b4b29bfbc99e86437d7266ce1df51186f72c0baef754d39a0dac1aef. Its safe source projection is merged here and retained on the working branch. Existing GPU execution records are unchanged.

The complete focused suite passed 137 tests. A cold server rehearsal verified the actual five collections and refused whole-plan acceptance, then exercised ordinary review admission and duplicate refusal against disposable ledger copies. Every historical charge event and reset record stayed unchanged; the existing UTC-day counter rollover was checked separately from lifetime call rows. Earlier harness failures are preserved privately. No model/provider call or live ledger mutation occurred during these tests. Judgment: implement only the exact one-review scope agreed with Claude, retain the final pair, and obtain independent implementation approval before installation. That review approved with no blocking findings. Held installation and one-use activation passed; one server-side scientific-review request is now preparing through normal admission. No model was running at the latest observation, and no GPU is running.

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

Operational judgment: an upload command wrapper initially used the wrong JSON spacing for its expected job ID and refused before dispatch. The wrapper was corrected to the native identity, both prepared job IDs were cross-checked, and upload then completed once. Original error and intent preserved; no installed code, admission check, charge or model-call change.

Billing reconciliation: B200 completed-hour compute is $2.00291173. Its original $16.5924 reservation and $10.039474 conservative closed-attempt bound remain recorded. No additional credit is claimed from partial hourly billing; uncertain/open reservations are untouched.

Real interruption evidence: first smoke segment completed epoch 0 (native rounded log duration 159.8 seconds), then stopped with a positive termination receipt and exit code 137. The full checkpoint proof has next_epoch=1 of total_epochs=5. The original interruption event, stop intent, observation, termination record and preserved $16.5924 reservation were cross-checked. Aggregate interruption record hash: 6e41b30824ef939e6b314bf7c548a84d8025acdc4bb74b93e08cfac13ed408f4. The subsequent collected continuation now proves completion after resume; independent scientific acceptance is still pending. No extra launch or repeated termination occurred.

Judgment: reuse the existing read-only progress and reservation replay tools for the admitted continuation, without an installed change, new watcher, launch or model call. Claude consultation was not needed for these observations; the approved control and latest PROCEED direction remain unchanged.

- docs > ITEM4_SMOKE_REVIEW_CHECKPOINT_PRIVATE.json: EXCLUDED_RECORD_PATH, PRIVATE_RECORD_PATH.
- orchestrator > item4_smoke_review.py: INFRASTRUCTURE_OR_CREDENTIAL_PATH.
- tests > fixtures > item4_smoke_review_prior_unit_PRIVATE.txt: EXCLUDED_RECORD_PATH, INFRASTRUCTURE_OR_CREDENTIAL_PATH, PRIVATE_RECORD_PATH.
