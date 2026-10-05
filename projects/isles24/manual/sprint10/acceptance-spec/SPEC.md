# Result card — Sprint10 known-case acceptance proposal

**Question:** Can the selected comparison-only notebook reproduce the preserved Sprint10 tables from completed Sprint8/9 runs under the predeclared acceptance contract?
**Evidence:** Inspected the complete selected source and saved output transcript identified below. Historical outputs report 100/100 fold tables complete, 50/50 matched-amount combinations paired, 990 matched-amount rows and identical compatibility checks across 10 partitions.
**Limitations:** These are externally saved known results, not a collected acceptance return. No private inputs, original CSV bytes, package manifest, execution receipt or deterministic acceptance result were supplied for this attempt. No execution, fresh measurements, literature search or independent review occurred here. All science remains exploratory.
**Next decision:** PROPOSAL_ONLY — submit this exact specification and selected notebook to bounded opposing review; subsequently assess the source-bound manual return through the existing system. This document grants no launch, acceptance, amendment or human ratification.

run_id: sprint10-stepd-a9123b81e3ef32ee
notebook_code_sha256: f2d78ef52b1238dbd865c4e35bc5b56bc960d9c85dea15dd7e2146ae53f85eca

## Scope and inspected evidence

- Selected source: `evidence/e2f6d75d5d2b213594c8a1b29b89c32b79f3813a474937888b53185c88d1b224-notebook_source.txt`, SHA256 `e2f6d75d5d2b213594c8a1b29b89c32b79f3813a474937888b53185c88d1b224`. Inspected all 986 lines: configuration/capture 23–96, shared utilities, compatibility, validation, matched-amount scoring, summaries, maps and final private export. Its text-file hash is distinct from the binding notebook-code hash above; the flattened source does not independently establish notebook cell serialization.
- Saved outputs: `evidence/6faa89dc1ee2ffdcdc5ffbab55a514f84908900353a114fb09e8e552cf39368e-result_tables.txt`, SHA256 `6faa89dc1ee2ffdcdc5ffbab55a514f84908900353a114fb09e8e552cf39368e`. Inspected all output entries, including cells 4/5 compatibility/completion, 7 pairing, 9 tables/contrasts and 11 map-save message. These belong to the historical baseline, not this package's execution.
- Supplied current-artifact contents: configuration, data contract, baseline bindings and validator were read in the stage input. Their logical paths are provenance references, not additional standalone files inspected here. The data contract still says `PROPOSED_SOURCE_REPAIR_NOT_EXECUTED`; historical outputs do not resolve that status.

Missing system records are absent, not size proxies. Preserve P001, task921, all earlier attempts and original results. Formal047 and implementation review047 remain distinct.

## Frozen scientific contract

Target: follow-up infarct tissue; primary scientific readout: patient-mean full-truth Dice and matched differences. System endpoint: reproduction of required tables/statuses. No fitting, tuning, new membership or cache construction. Defined training/probing utilities are not invoked by the comparison path; do not call them.

Use precisely the existing 99 development cases selected by the pinned split manifest minus the one pinned exclusion. Retain `assert len(CASES) == 99`. Keep the 25 final-evaluation and 24 reserve patients untouched. No outcome-based membership amendment or reading of their images/outcomes is allowed. Private split membership verification is confined to the existing manual lane; no membership or patient payload enters this stage workspace.

Preserve these configuration pins:

- Tree predecessor: `sprint8-seeds-features-PRIVATE/run-875c56c278` (r3 continued by r4); network predecessor: `sprint9-unet-PRIVATE/run-0a60362503`, FULL protocol, never SMOKE.
- Drive base `/content/drive/MyDrive/isles-pilot`; existing cache `feature-cache-2mm-v2`. Feature configuration: target 2.0 mm, vessel percentile 98.0, core threshold 0.30, penumbra Tmax 6.0, schema `isles24-features-2mm-v2`.
- Original repository reference `https://github.com/Moroseui/concept-research-scout`, commit `c17281a11dd2ed15e59cc38bbb526fb6c466b145`. Preserve separately from the package's actual source binding; do not substitute HEAD or fetch new code.
- `CODE_VERSION = sprint10-r2-exclusion-reference-v1`; map shuffle 101 and seed 1; score probability tolerance `1e-6` (distinct from table-comparison tolerance).
- Private input directory `sprint10-inputs-PRIVATE`; `split_manifest.csv` SHA256 `da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843`; adjacent `excluded_cases.json` SHA256 `ee8d4f96b0c16620450c0e7e2e6a56993d2ee68e20913c78a1bb8fe7af0f1ab2`, count 1. Keep membership out of configuration and reports. Verify hashes, unique nonempty exclusion strings, count, adjacency and no symlink; bind hashes/count into the comparison identity.

Admission imaging/baseline clinical inputs remain distinct from post-intervention mTICI/recordedness. The latter cannot support admission-time or causal claims. Clinical outcome prediction is a later aim.

## Computation and statistical invariants

Read completed run manifests, execution records, partitions, fold tables and saved scores. Require current cache content identities, exact 99-case lists, grid, shuffles/fold count and complete partition dictionaries to agree; require exact planned partition keys and FULL protocol. Compare clinical parsed-table digest, field sets and header mapping separately. A discrepancy disables the notebook's cross-pipeline clinical contrasts, but also prevents acceptance against the complete pinned baseline.

Keep fold/score validation of fingerprints, requested shuffle/fold/seed, exact recipe-patient sets, smoothing width, training length, array shape and finite probabilities. Preserve metric-specific NaNs; reject infinity. Report complete/pending/invalid/skipped and paired/unpaired. Missing execution records or arm lists remain absent despite code fallback defaults; reconcile without retraining.

Smooth saved network scores with recorded width and select matched D predicted amount, never true volume. Preserve rounding/clamping and score-descending, voxel-index-ascending ties. Evaluate full lesion truth, including outside-mask lesions. Preserve all metrics, empty-mask rules, valid counts, recipes and contrasts. Dice/voxel F1 differs from lesion-wise F1 (26-connectivity, greedy matching at IoU >=0.2, both-empty 1).

Average valid repeats within patient before descriptive summaries. Match contrasts on shuffle, fold, training seed and patient, subtract first minus second, then average differences within patient. Bootstrap patients, not observations. The volume contrast is the median of patient-mean absolute-error differences, not a subtraction of the two descriptive medians.

Freeze the actual summary implementation: one `np.random.default_rng(0)` stream, 2000 resamples per statistic, replacement sampling of the ordered patient vector and NumPy 2.5/97.5 percentiles. The descriptive recipe summaries consume draws first. Each contrast then consumes Dice-mean draws, volume-median draws and lesion-F1-mean draws in that order. Preserve group, patient, arm and contrast ordering and all filtering/formatting. Do not reset the seed for each statistic, vectorize/reorder bootstrap calls or substitute the separately defined helper. Preserve the 12 historical contrasts; do not add clinical-versus-U_base contrasts in this acceptance run.

## Proposed manual procedure and resource boundary

After applicable review/system gates, use the exact packaged notebook in existing manual Colab CPU entitlement with existing dependencies/cache and completed Sprint8/9 runs. No paid resources, GPU, installation, source edits, deployment, main merge or model clients. Budget: one comparison/bootstrap/map/export pass, zero fitting or discretionary retries. No measured resource usage or wall-time/RAM cap is supplied; do not invent it. Stop on exhaustion or required resource expansion.

1. Before Run All, require the manifest to bind actual source, exact reviewed spec bytes/hash, notebook code hash/cells, review hash, private hashes, seven baseline pins, tolerance and run identity. Missing bindings stop dependent use; this proposal does not manufacture them.

## Acceptance and difference accounting

Use the supplied original-baseline bindings (seven SHA256 pins) unchanged; baseline bytes must match those pins, not merely the transcript. Require exact return set, receipt/manifest/start binding, original and actual hashes, predecessor identities, unchanged 99-member set, expected private-input identity/fingerprint and output paths. Require preserved baseline JSON key sets and only the declared added identity keys in new JSON. A receipt's `training_performed: false` alone is not independent execution proof.

Predeclared comparison contract:

- `numeric_atol = 1e-10`; `numeric_rtol = 1e-09`.
- `bootstrap_resamples = 2000`; `bootstrap_seed = 0`; algorithm and order unchanged.
- Strings, counts and formatted intervals: exact. Row and column order: exact.
- Permitted path difference: only original/new comparison output directory prefix.
- Permitted metadata differences: only `utc`, `code_version`, `fingerprint`, `run_identity`.

Explain every difference: UTC capture time, selected code-version identity, fingerprint/run_identity binding to unchanged predecessors and pinned private references, and isolated output prefix. Allowances never cover changed science, membership, predecessors, cache, partitions, clinical identity, counts or statuses. Numeric changes need tolerance compliance and explanation; other formatting must match. No sorting, arbitrary path normalization, tolerance changes or output repairs to force a pass. Validator output is necessary but does not replace checking the full contract.

## Known results, limitations and next decision

Historical output cell 9 reports D Dice 0.206, U_base smoothed 0.204; matched difference -0.002 (-0.019 to +0.014), median patient absolute-volume-error difference +11.1 ml (+6.9 to +14.0). At D's amount, Dice difference is -0.010 (-0.023 to +0.003), with zero volume-error difference. These are exploratory historical results, not fresh measurements, equivalence or new efficacy evidence. Reproduction establishes known-case consistency only.

Keep prior 69/30 development exposure, partly annotation-assisted cached representation, mask-constrained predictions, clinical timing/missingness, unequal repeat coverage, only seed 1 for clinical network arms, two baseline seeds without a training-variance estimate, and unrun locked evaluation explicit. Whole-pipeline differences do not isolate architecture or spatial context. Maps are outcome-selected illustrations, not independent evaluation. No literature-dependent novelty claim is made.

Older findings remain open without exact recorded resolution. Source checks addressing S10-R4-01–04 are not closure receipts. Sprint9 resume/identity/parser/reporting concerns are not repaired here. Preserve their scope/history; deprecation warnings are advisories absent demonstrated failure.

Next decision: **PROPOSAL_ONLY**. Opposing review has at most two rounds. No review verdict is authored here. A reviewer uses REVISE only for a concrete blocker and includes `BLOCKER[category]` in its rationale, with category exactly one of: test-set/leakage, code/spec mismatch, metric/statistic, privacy/secret, budget, execution authority/provenance. Record evidence/version, verified/inferred/untested status, consequence, affected task and smallest correction. Other concerns remain advisories. APPROVE must not conceal an unresolved blocker and does not itself execute or scientifically accept results. Any nonpermitted difference blocks acceptance; after two rounds retain unresolved findings and stop dependent progression. A future valid return still requires formal interpretation/review and a separate recorded system disposition, without human ratification invented here.
