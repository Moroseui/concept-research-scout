# Result card — prospective external-seed P001 adoption

**Question:** Is fixed admission Tmax >6 s an adequate minimal reference for follow-up infarct prediction?
**Evidence:** Supplied P001 v1.1 fixes a no-fit threshold, patient-level evaluation and integrity rules; a historical Claude review records APPROVE. Current status reports no real return.
**Limitations:** Performance is unknown. Hypoperfusion is not final infarct; treatment, units, registration, selected cohort and prior outcome use constrain interpretation.
**Next decision:** **ADOPT_CONDITIONALLY** as a minimal exploratory reference under the proposed prediction charter. Ratification, baseline launch and any backend amendment remain pending; this is not an approval.

## Scientific disposition

P001 asks: how well does a fixed admission Tmax >6 seconds mask agree with the released MRI-derived follow-up infarct mask in NCCT space across the frozen eligible 99 development cases, after observed treatment? It provides a transparent spatial-overlap and volume-bias reference before investing in fitting. Its scientific value is a reproducible reference measurement, including an honestly poor result, not trained-predictor performance or novelty.

This is adequate as the campaign's **minimal reference**, not evidence that it is a competitive or clinically adequate predictor. Admission hypoperfusion may include tissue that survives; later infarct depends on treatment and subsequent care. Whole-grid evaluation, small lesions and registration can affect Dice. No causal, untreated-infarct, model-use, clinical deployment or external-validation claim follows. The specification's 2–9 day timing statement remains attributed to that document; supplied newer metadata verification explicitly does not verify full-text timing or units.

Conditional adoption is preferable to AMEND now because no valid patient evidence or verified contradiction establishes a scientific defect needing changed bytes. REJECT would discard a useful transparent reference merely for not being fitted. If unit evidence contradicts seconds, inputs violate finite/geometry requirements, or the intended question changes to clinical outcomes or a learned predictor, stop and propose a separately versioned amendment or comparison; do not repair P001 silently. No performance threshold or alternative is selected here.

## Frozen scientific contract

Retain exactly P001 v1.1: lexical IDs from only `case_id` in the frozen cohort table; one canonical admission Tmax and one ses-02 NCCT-space lesion per ID, 198 selected members; reserved 49 untouched; size/CRC verification before opening and archive verification if used. No rank-based selection, whole-archive extraction or extra case exclusion.

Predict finite 3D Tmax >6.0 on the full released grid, no fitting or filtering; any nonfinite voxel stops the run. Write each prediction before label opening. Require finite binary 3D labels, positive voxel volume and shape/affine agreement (atol 1e-5, rtol 0); no resampling. Primary: equally weighted mean patient Dice, both-empty=1 and one-empty=0. Secondary: median Dice, mean absolute and signed prediction-volume error in mL. Uncertainty: 2,000 patient bootstrap resamples, seed 20260905, central percentile 95% interval, conditional on reused development cases.

Keep one CPU Colab run, 60 analysis minutes, separate staging receipt and at most one staging invocation per new output path. Preserve failures, original console and checkpoints; reuse only identically bound, byte-verified checkpoints. Complete means exactly 99 patients. No new GPU, training, search or paid provisioning. Private inputs, IDs/paths, manifests, predictions and per-case metrics stay private. Publication manifest remains exactly the five required/allowed files: `summary.json`, `resolved_config.json`, `environment.json`, `execution_receipt.json`, `RESULT_CARD.md`; any broader campaign publication policy does not expand this manifest.

## Preserved identities and origin

All identities below are transcribed from supplied records, not locally rehashed. Preserve every frozen artifact and all historical authorship, decisions and approvals; do not regenerate `run.py`. The system authors only this prospective assessment. P001 was externally seeded and operator-delegated; its recorded investigator/build actor is Codex, GPT-6 Astra, with delegated campaign authority. Its historical opposing reviewer is Claude, `claude-fable-5`.

| Binding | Frozen identity |
|---|---|
| Campaign SHA-256 | `7350da8a2b6f883393ef997963df5821fa25f027e776d31adaa2f26cd4b4fb32` |
| P001 spec SHA-256 | `d76cf92b35c8aabe443b91d734285af2e5653de00bbadc13360e87fa6e45f56c` |
| P001 code SHA-256 | `d54e3ea5c45c0d47fe8bace014058e1660d92b72abc36cc2fdc077acae3d47b0` |
| Investigator decision SHA-256 | `78da702da6a340da79a242aa049b64009b4b954a215e22fc1387212390dce68e` |
| Review SHA-256 in build receipt | `18f6ace723871d9319a5eda995ffb99389af46bb95cd50b1e97e1a63d326d727` |
| Reviewed commit | `469d29df002ea78f64146731244769d7c82330d6` |
| Cohort table SHA-256 | `aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9` |
| Archive manifest Git blob | `edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2` |
| train.7z size / MD5 | `99014629647` bytes / `36ae28b9a17f7340b8bbef62b595cb57` |
| Original snapshot | `0770c7dcabe781cbfb87de505755e7aafa758f2e` |
| Scientific source commit | `d6a1184b4378e849213fd887a6f7b103fb1a64d5` |
| Notebook commit | `1a81c037343598f4e4585153b11d761b87a9ae3a` |

The full supplied `review.json` file inventory, execution/response hashes, `build_receipt.json`, `investigator_decision.json` and `publication.json` remain authoritative historical records; this table is not a replacement inventory. The spec's pending-review text and decision's `FIX_SPECIFICATION_PENDING_OPPOSING_REVIEW` are historical bytes; later review records APPROVE. Neither is rewritten. That approval is bound to its reviewed source, not blanket approval of changed HEAD dependencies.

047 Phase A remains at `probes/047/results/results_v2`, blob `b4887c05a21bfe870589b5d9982066943df679d5`; preserve all 047 artifacts, original approvals and authorship. Phase-B intended historical destination remains `probes/047/results/results_v2-dc586665d0be`. No import, rerun, ratification, fabricated console or 047 acceptance dependency is proposed.

## Conditions and evidence for the next decision

1. Review the exact proposed charter/rubric/prompt/adoption texts. A future prospective record must name their final paths, versions and SHA-256 identities, the unchanged P001 spec/code, original decision/review, and a new adoption-review identity. Those new bindings are pending, not fabricated here; never overwrite historical lineage.
2. Resolve claim-specific source gaps, particularly Tmax units and timing/label provenance. Document residual assumptions and whether evidence supports unchanged P001 or requires amendment. No fresh source inspection is claimed here.
3. Establish an authorized execution snapshot and fresh opposing review of affected dependencies, including changed scout/publisher/transport surfaces where applicable. Reconcile blocked dispatch, remote processes and checkpoints before deliberate hold resolution. Historical archive read-back proves historical identity, not current runtime access. Launch remains separately reserved.
4. For scientific interpretation, require all five permitted return files, exact binding validation, exactly 99 completed evaluations, original private console/checkpoints and failure history, uncertainty and volume bias. Unavailable measurements stay null. Invalid/partial execution cannot support a negative conclusion. Only then consider one follow-up at a time within the two-comparison cap.

Sources: supplied `campaigns/isles24-pilot/experiments/P001/{SPEC.md,run.py,build_receipt.json,investigator_decision.json,review.json,publication.json}`; campaign `CAMPAIGN.md`; `docs/science/PREDICTION_READINESS_DIRECTION_20260906.md`; `docs/science/PREDICTION_PRIMARY_SOURCES_20260906.json`; `docs/isles-pilot/{CURRENT_STATUS.md,047_LIFECYCLE.md}`. The Wednesday path and missing onboarding/deployment originals are disclosed in `CHARTER.proposed.md`. No original repository or patient evidence was sought.
