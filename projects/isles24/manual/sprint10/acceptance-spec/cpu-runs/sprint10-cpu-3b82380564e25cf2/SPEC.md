# Sprint10 server CPU known-case reproduction — proposed run specification

Question: Can the CPU adapter exactly reproduce the completed Sprint10 comparison?
Evidence: Source and saved outputs [N,O] were read and hashes verified; historical measurements appear below. No experiment ran here.
Limitations: Private assets, baseline CSV/JSON bytes, installed environment, notebook package and CPU receipt are unavailable here. Historical acceptance is not fresh validation or authority.
Next decision: Independent review of this spec/package, then separately admitted CPU execution only after all gates pass. This is a proposal, not launch permission.

run_id: sprint10-cpu-3b82380564e25cf2
notebook_code_sha256: 26d425e1e9193c753c8b23ef28e49a7b637443ae4ea87cf333a6831f32512055

## Inspected evidence and scope

[N] `evidence/91dc9c8fba7f5876cc61fcb02b40f7f395d4524711daad7bea253907fb6ed0f5-notebook_source.txt`, SHA256 as filename prefix; all 976 lines read. Configuration/capture: 13–138; comparison: 682–922; maps/return: 925–976. Its verified text hash differs from the binding code-cell hash above, which must be verified against the emitted notebook.

[O] `evidence/6faa89dc1ee2ffdcdc5ffbab55a514f84908900353a114fb09e8e552cf39368e-result_tables.txt`, SHA256 as filename prefix; all 186 lines read. Historical cells 4/5/7/9 contain compatibility, completion and measurements. Console tables cannot substitute for baseline CSV bytes.

[B] `prompt.md:832–907`: embedded current cpu-configuration, cpu-input-binding, baseline-bindings and cpu-metric-contract artifacts, read with supplied hashes. [V] `prompt.md:926` onward: embedded current/validator.py v2, including CPU adapter/data verification and validate_cpu_return. Embedded contents were inspected, not executed; separate files are unavailable.

Scope: current task and supplied AUTONOMY20260927-m2/stops/caps. Server CPU in the existing sandbox under the designated unprivileged worker only. No Colab, GPU, training, model calls, spending, downloads, installation, extraction, tuning, new arms or locked-patient access. Preserve task921, prior attempts, P001 and predecessors. Reproduction is not new efficacy, clinical utility or successor authority.

## Exact inputs and runtime contract

Use only the verified private development-only transport: 759 assets, 99 distinct cases. Bind `manifest.json` SHA256 `6ecc6a37c21fff928721b8cf83853cfbf58ee193800c2dca6f0fa325db1efdde` and `development99.manifest.json` SHA256 `45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86`. Verify full inventory, every file's size and hash, cohort linkage and exact membership before mounting inputs; refuse symlinks, traversal, missing and extra files [B,V]. No access to the 25 final-evaluation or 24 reserve patients, including copying their files or the original mixed-membership split.

Derive `/workspace/inputs/split_manifest.csv` solely from that verified cohort: header `case_id,population`, sorted cases each marked `census`, CSV newline `\n`, SHA256 `3ace11512d345b2cc0d8e78cf95b98f9f4afe45c581a1d4ab1f38c81cd3fd615`. Beside it, `/workspace/inputs/excluded_cases.json` is the pinned empty list, count 0, SHA256 `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`. Verify both hashes, reference fields, list type/count/uniqueness and adjacency; retain `assert len(CASES) == 99`. Empty exclusions are correct because the verified cohort already omits the originally excluded census case. This is not removal of an exclusion from a mixed cohort. Preserve predecessor split/exclusion identities in [B] as provenance only.

Mount the verified server assets read-only at the legacy virtual prefix `/content/drive/MyDrive/isles-pilot`; this path is not a Drive/Colab connection. Use `feature-cache-2mm-v2`, Sprint8 `sprint8-seeds-features-PRIVATE/run-875c56c278`, Sprint9 `sprint9-unet-PRIVATE/run-0a60362503`, and original comparison `sprint10-comparison-PRIVATE/compare-875c56c278-0a60362503` beneath that prefix. Inputs and prior results remain immutable.

Preserve FEATURE_CFG, map shuffle/seed and repository reference exactly as [N:13–30]; CODE_VERSION `sprint10-m2-cpu-adapter-v1`. Do not fetch the repository. Use the registered hash-verified CPU environment; record its digest, Python and dependencies including xgboost/matplotlib. Versions are unavailable here. Missing dependencies or environment binding stop execution; no installation.

Read-only `/package` must bind notebook, spec, review, source, code cells/hashes, data/baseline/private-file identities and comparison contract. Execute exact cells once, in order, in a fresh process. Training/cache-building helpers in [N] stay inert: no fitting, probes, cache regeneration, tuning or repair fallback.

Output: `/workspace/comparison/compare-875c56c278-0a60362503-<fingerprint>`; return: `/workspace/return`. Use [N,V] canonical sorted-JSON identity hash truncated to 12 hex digits, binding CPU code_version, both predecessor fingerprints and derived split/exclusion hashes/count 0. No predecessor writes.

## Scientific procedure held fixed

Target: follow-up infarct tissue. Age/sex/admission NIHSS are baseline fields; mTICI/recorded-status are post-intervention explanatory fields, not admission predictors or causal treatment evidence.

Keep [N:721–816] checks unchanged: equal cache identity, exact 99-case lists/grid/shuffles/folds, complete partition dictionaries and planned keys, smoke=False; compare clinical digest/fields/mapping. Missing/invalid/skipped/unpaired work or clinical mismatch fails this complete-baseline reproduction even if the notebook emits provisional reports.

Validate every expected fold table's fingerprint, shuffle/fold/seed, unique exact recipe-case set, required finite metrics, no infinity and conditional NaN domains. Validate score archives' readability, fingerprint/arm, filename partition/seed, smoothing grid, positive best_epoch, exact held cases, array shape, finite probabilities within PROB_TOL=1e-6. This input tolerance is not output tolerance. Refuse invalid inputs; no retraining.

Reconstruct matched-amount arms from saved network scores, fixed smoothing and tree D's predicted volume on the same patient/shuffle/fold/seed, never true lesion volume. Preserve lexicographic ordering: descending score, ascending voxel index. Score Dice/voxel F1, lesion-wise F1, recall, volumes and surface distance against complete lesion truth; preserve feature-mask AUROC/AP and specificity domains, empty-region rules, mask coverage and all valid counts. Both-empty Dice/F1=1; undefined conditional metrics remain NaN, never substituted with zero [N:648–678,746–816].

Export all 22 historical recipes and all 12 predeclared contrasts, without selecting a winner or adding comparisons. Descriptive summaries average valid repeats within patient first. Contrasts match shuffle/fold/training seed/patient, compute first-minus-second differences, then average repeats within patient. Dice and lesion-F1 contrasts are means over patients; volume-error contrast is the median of within-patient mean differences in absolute error, not a difference of marginal medians.

Preserve the reporting cell's single `np.random.default_rng(0)` stream, 2,000 resamples per statistic and percentile endpoints 2.5/97.5. Preserve recipe order, contrast order and RNG consumption (including lesion-F1 intervals). Do not reseed each contrast or replace this stream with the separate helper's stream. Patient bootstrap is exploratory, conditional on saved predictions; repeated observations are not independent patients [N:877–919].

## Mandatory comparison and return

All five CSVs must be byte-identical, including row/column order, quoting, precision, missing-value serialization and newlines. Numeric tolerance is zero; no CSV path normalization or approximate equality can pass acceptance. Expected original SHA256:

| File | SHA256 |
|---|---|
| completion.csv | 150231afb5fa4659e053bf6e5b6ceffa47c1460643c379467eed99c840385447 |
| matched_amount_status.csv | faa1c29ccedf3a81a0e5431ee11ee02fa5511a0b5750b6d2c277b19e916443b6 |
| summary_by_recipe.csv | 51c30fd96f55a0fcfc076351fedeea7b17d9ddbee900d4f616c22f8bdc6d1348 |
| paired_contrasts.csv | 0056c3967a43d97def92abad4af4d97c683fa2af992e87e2539bce93a57c7073 |
| all_percase.csv | ca6a08951e2453c1ccdeab9d7513f3f63332d24179097d751913f589d19e9df9 |

Original JSON hashes: comparison_reference.json `d7e8e4f8f95a56a4e83b7ea75e0575a46d4b8df2e61046587b72681116b69aa6`; compatibility_report.json `7c7e3aebfcde612b7922207bb3a959c642acaa59130e1820ad362e1600d32fab`. Parsed scientific content must match exactly. Only top-level utc, code_version, fingerprint and run_identity may differ; their new identity values must satisfy this specification. Preserve nested predecessor paths/identities and the exact baseline key sets plus fingerprint/run_identity. Metadata allowance never excuses scientific differences [B,V].

Use `validate_cpu_return`, including its final raw-byte checks; the legacy approximate `compare_tables` result alone is insufficient. Require exactly baseline/actual copies of these seven files plus started.json and execution_receipt.json, all regular files. Verify baseline hashes before/after computation, manifest/start/receipt bindings, exact 99-case equality, training_performed=False, matching CPU tolerance, output path, identity and fingerprint. Maps and private example aliases remain outside the return and private; they are not additional equality targets.

## Historical measurements and interpretation limits

[O, cell 9] reports 100/100 fold tables complete, 50/50 score files complete, 50/50 matched-amount combinations paired, 990 matched-amount rows and nonprovisional status; 10 identical partitions and clinical compatibility passed in cell 4. These are historical reported checks, not observations of the proposed CPU job.

D Dice was 0.206 (exploratory 95% interval 0.169–0.247); smoothed U_base 0.204 (0.164–0.244). Their matched Dice difference was -0.002 (-0.019 to +0.014), 99 patients/396 observations; median patient absolute-volume-error difference +11.1 ml (+6.9 to +14.0). U_base at D's amount minus D: Dice -0.010 (-0.023 to +0.003), 99/396, volume-error difference 0.0 ml. Post-intervention smoothed network Dice was 0.220 (0.180–0.266); its matched-amount contrast against D was +0.003 (-0.010 to +0.017), 99/198. No superiority/equivalence is established. Retain every variant [O, cell 9].

Advisories: development-outcome exposure (including 69/30 history), annotation-assisted caches, mask constraints and pipeline differences limit inference. Clinical network arms have seed 1; baseline has seeds 1/2. Clinical-versus-tree contrasts do not isolate clinical gains; matched clinical-versus-U_base evidence would be needed. AUROC/AP have 97 valid patients, recall/ASD 98 in displayed tables. No untouched-test, generalization, mechanism, novelty or clinical-use claim. Older S9/S10 findings remain open absent exact recorded resolutions; inspecting r2 validation does not close upstream training/provenance findings.

## Stopping, budget and disposition

One admitted CPU attempt, one run at a time; no model calls or paid compute in execution. Reconcile the run ledger first. Existing start/return or uncertain/completed attempt means stop and reconcile, never rerun to fill a gap. Preserve refusals, logs and partial outputs. Stop on identity/hash/cohort/environment failure, missing baseline, invalid input, any byte/scientific JSON mismatch, resource limit or human halt. Never relax tolerance, overwrite originals or silently change code. Bind executor resource limits before dispatch; duration/RAM limits are unavailable here. Record elapsed time/resources; unavailable cost/intervention/token measurements are null. Historical timings are not CPU benchmarks [O].

Readiness/success are unverified. A later REVISE must name BLOCKER[category]. Comparison success requires independent review and grants no further run.
