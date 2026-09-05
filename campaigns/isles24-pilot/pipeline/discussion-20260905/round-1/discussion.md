# P001 baseline discussion proposal

This is a bounded, agent-authored discussion proposal based solely on the supplied campaign, P001 v1.1 specification, publication policy, and implementation text. No result exists yet. It is neither an approval nor an executable amendment, and it does not authorize execution or select a follow-up. The campaign records delegated operator authority; that record is not fresh human ratification of this document or any result. P001's specification is fixed before execution, with opposing-family review pending in the supplied record. No patient data or original repository was accessed, and no experiment was executed for this discussion.

## Baseline question and admission timing

The baseline question within the authorized campaign is: how well does a fixed admission Tmax > 6 seconds tissue-at-risk map predict the released follow-up infarct mask in the frozen 99 development cases? P001 is a transparent threshold baseline with no training or fitted parameters. Its purpose is to measure how much admission hypoperfusion alone captures of the later observed infarct, without claiming state-of-the-art performance.

The only prediction input is the admission NCCT-space Tmax map, available by completion of admission CT. Prediction uses the full released Tmax grid with a strict > 6.0 seconds threshold, without erosion, connected-component filtering, or a lesion-dependent mask. Every Tmax voxel, including background, must be finite; a NaN or infinity stops the run. The seconds convention is inherited from the inspected prior implementation and remains a metadata assumption that must be reported.

The operational target is the released binary MRI-derived follow-up infarct mask in NCCT space, measured after observed treatment. The supplied specification reports MRI at 2–9 days. This target is a later imaging surrogate, not histological ground truth or the infarct that would have occurred without treatment. Each prediction mask must be written before its label is opened for evaluation. Follow-up MRI intensities, lesion-derived features, clinical outcomes, post-treatment variables, and contribution rankings cannot inform prediction.

## Frozen identity and evaluation

The original pins remain unchanged:

- Specification: P001 v1.1, including the pre-execution clarification that all Tmax voxels must be finite.
- Cohort source: only the `case_id` column of the idea-046 contribution table, SHA-256 `aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9`; exactly 99 unique IDs, sorted lexically, with all other columns discarded.
- Archive member manifest: git blob `edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2`.
- If `train.7z` is used: 99,014,629,647 bytes and MD5 `36ae28b9a17f7340b8bbef62b595cb57`.
- Selection: exactly one admission Tmax derivative and one canonical ses-02 NCCT-space lesion derivative per eligible ID, using full manifest paths; exactly 198 selected members. Ambiguity fails selection. No whole-archive extraction, noncanonical duplicate lesions, or access to the 49 reserved cases is permitted.
- Uncertainty: 2,000 patient bootstrap resamples, seed `20260905`, central percentile 95% interval for mean Dice.
- Compute envelope: one CPU Colab run, at most 60 analysis minutes, with archive verification/extraction separately receipted and at most one staging invocation per new output path; no GPU, training, paid provisioning, or hyperparameter search.

Each selected compressed input must pass recorded size and CRC32 checks before opening. Evaluation requires finite 3D arrays, binary labels in {0,1}, positive voxel volume, and matching shape and affine with absolute tolerance 1e-5 and relative tolerance 0. Geometry disagreement stops the run; no post hoc resampling or extra case exclusion is authorized.

The primary metric is the arithmetic mean of per-patient volumetric Dice, giving each of the 99 patients equal weight. Both masks empty yields Dice 1; exactly one empty yields 0. Secondary descriptive metrics are median Dice, mean absolute lesion-volume error in mL, and mean signed prediction-volume error (prediction minus label volume). All 99 cases are evaluated once as exploratory development cases. No training/validation split is needed because nothing is fitted, but that does not make this an untouched test set.

## Exploratory interpretation and limitations

A future valid result would describe agreement between a fixed admission hypoperfusion threshold and the observed later infarct in these selected cases. Admission-only signal cannot determine treatment-dependent final infarct: reperfusion and subsequent care are unmodeled. Hypoperfusion may include tissue that survives, while small lesions and registration errors can depress Dice. Signed volume error describes volume bias but cannot by itself establish its biological cause.

The cohort's selection, prior use of development outcomes, scanner/site heterogeneity, acquisition and reconstruction differences, and inherited units assumption limit interpretation. Reusing only cohort membership avoids using contribution rankings as features; it does not erase selection effects or prior outcome use. The bootstrap interval describes patient-resampling variability within these 99 cases. It does not provide external validation, causal uncertainty, or correction for repeated development-set use. A headline must not be selected by significance. No biological mechanism, model-use, or clinical-deployment conclusion is licensed.

## Evidence required before interpreting any result

The following are evidence requirements under the existing specification, not instructions to execute work or amend it:

1. **Authority and identity:** an agent-attributed decision binding the exact campaign/specification bytes, and opposing-family review of both specification and executable implementation before a real run. The supplied record does not establish completed review. Actual spec/code/review bindings must be evidenced, not invented from this discussion.
2. **Input scope and timing:** an auditable record of the pinned cohort and manifest checks, unambiguous 198-member selection, compressed-file integrity verification, archive identity where applicable, and exclusion of reserved cases. Evidence must support admission-only prediction and prediction persistence before label opening, without outcome-dependent selection or features.
3. **Implementation validity:** review and validation evidence that the executable implements the strict threshold, fail-on-nonfinite policy, geometry and label checks, voxel-volume conversion, empty-mask conventions, patient weighting, and pinned bootstrap. The inherited Tmax units assumption must be disclosed; an implementation-unit failure invalidates the run.
4. **Complete and valid execution:** evidence of exactly 99 completed cases, compliance with the compute cap, environment and machine/agent identity, execution and staging durations, and the original console. Any reused checkpoints must be byte-verified with identical spec/code/input bindings. All attempts, failures, and partial checkpoints remain on record. Identity, scope, input-integrity, geometry, unit implementation, or output-identity failures stop the run and scientific claims until resolved. A failed or incomplete run is not a negative result.
5. **Consistent reporting:** the required aggregate bundle—`summary.json`, `resolved_config.json`, `environment.json`, `execution_receipt.json`, and `RESULT_CARD.md`—must agree on identity, completion, metrics, uncertainty, and limitations. The result card must state the question, unchanged baseline, admission timing, result and uncertainty, limitations, and artifact references. Available usage is recorded; unavailable cost, token consumption, or human-intervention measurements remain null. Generated files alone do not establish that the underlying run passed every requirement.

Private manifests, patient IDs/paths, per-case metrics, predictions, masks, staged inputs, and checkpoints remain private. Any permitted aggregate publication excludes those materials; reviewed console evidence is supplied separately for audit. This discussion neither publishes artifacts nor requests access to private evidence. With no result or execution evidence supplied, no performance estimate, uncertainty interval, success claim, negative finding, or follow-up proposal is made.
