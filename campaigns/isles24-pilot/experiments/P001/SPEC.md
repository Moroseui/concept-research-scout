# P001 v1 — admission hypoperfusion as a final-infarct baseline

Status: specification fixed before execution; opposing-family review pending.
Question: How well does a fixed admission Tmax > 6 seconds tissue-at-risk map
predict the released follow-up infarct mask in the frozen 99 development cases?
This is a transparent threshold baseline, not a trained model or claimed
state-of-the-art system. It tests how much a simple perfusion deficit already
captures, before investing in a fitted predictor. No follow-up comparison has
been selected or run.

## Target and timing

Operational target: the released binary MRI-derived follow-up infarct mask
in NCCT space, after observed treatment, evaluated on the full released Tmax
image grid. It is a surrogate measured days later, not histological ground truth
and not a counterfactual untreated infarct. Actual reperfusion and subsequent
care are unmodeled sources of uncertainty. The dataset paper reports MRI at
2–9 days. Predictions use only the admission NCCT-space Tmax map. Labels are
opened solely by evaluation after each prediction mask has been written.
No follow-up MRI intensities, lesion-derived features, clinical outcomes,
post-treatment variables or contribution ranks enter prediction.

## Frozen cohort, inputs and selection

The exact 99 eligible IDs are read ONLY from the case_id column of the pinned
idea-046 contribution table (SHA-256
aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9).
Sort IDs lexically, discard all other columns. This reuses cohort membership,
not outcome rankings. The frozen archive member manifest is git blob
edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2. Select exactly one admission
Tmax derivative and one canonical ses-02 NCCT-space lesion derivative per
eligible ID using full paths in that manifest. Ambiguity is a failure, never
resolved using outcome content. Noncanonical duplicate lesions are not staged.
Only these 198 members may be extracted. Reserved IDs never enter selection.
Verify each selected compressed file's recorded size and CRC32 before opening.
If using train.7z, first verify 99,014,629,647 bytes and MD5
36ae28b9a17f7340b8bbef62b595cb57. No whole-archive extraction.

## Baseline and evaluation

Predict finite Tmax > 6.0 seconds, with no fitted parameter, erosion, connected
component filtering or lesion-dependent mask. The threshold follows the prior
program's inspected Tmax convention; units remain an inherited metadata
assumption and must be reported. No training/validation split is needed because
nothing is fitted. All 99 cases are evaluated once as exploratory development
cases, with equal patient weight. This is not an untouched test set.

Primary metric: arithmetic mean of per-patient volumetric Dice. Both masks
empty gives 1; exactly one empty gives 0. Secondary descriptive metrics: median
Dice, mean absolute lesion-volume error in mL, and mean signed prediction-volume
error. Require finite 3D arrays, binary label values {0,1}, positive voxel volume,
and matching shape/affine (absolute tolerance 1e-5, rtol 0). No post hoc resampling;
geometry disagreement stops the run and requires a specified amendment.

Uncertainty: 2,000 patient bootstrap resamples, seed 20260905, central percentile
95% interval for mean Dice. This describes resampling variability within these
selected development cases; it is not external validation, causal uncertainty
or compensation for repeated prior use. Do not select a headline by significance.

## Budget, integrity and outputs

One CPU Colab run, at most 60 analysis minutes (archive verification/extraction
separately receipted; at most one staging invocation per new output path). No GPU,
training, paid provisioning or hyperparameter search. On input integrity, scope,
geometry, unit implementation, or output identity failure stop and retain the
original console and completed patient checkpoints. No extra case exclusion is
authorized: completion requires exactly 99. Reruns reuse only byte-verified
checkpoints with identical spec/code/input bindings. A failed run is not a
negative result. Per-case predictions and metrics remain private on Drive.

Permitted publication: aggregate summary, result card, configuration, environment
and execution receipt without patient IDs/paths; reviewed console is supplied
separately for audit. Private manifest, per-case metrics, masks and staged inputs
never enter a Git publication bundle. Record unavailable cost/usage/intervention
measurements as null. Follow-ups (maximum two) require a new versioned comparison
specification and review after baseline evidence is inspected.

## Verified sources and limitations

- Dataset and license: https://zenodo.org/records/16813698 (live API checked
  2026-09-05); 149 released training cases, distinct from the frozen eligible 99.
- Dataset paper: https://arxiv.org/abs/2408.11142 (follow-up and annotation source).
- Challenge paper: https://arxiv.org/abs/2408.10966 (prediction task and measures).
- Prior program implementation: probes/023/run.py, Tmax > 6 convention. This
  baseline does not inherit that study's outcome-selected region or rankings.

Admission-only signal is insufficient to determine treatment-dependent final
infarct. Hypoperfusion can overpredict surviving tissue; small lesions and
registration error can depress Dice. Selection of these 99 cases, scanner/site
heterogeneity, acquisition/reconstruction and prior outcome use limit scope.
No model-use, biological mechanism or clinical-deployment conclusion is licensed.
