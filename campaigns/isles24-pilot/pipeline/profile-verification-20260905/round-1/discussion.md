# P001 v1.1: future-profile integrity and result-return discussion

This bounded proposal describes the verification gates that must pass before a future P001 return could be interpreted. It uses only the supplied campaign, specification, publication policy and runner text. No result, execution evidence, decision record or completed review is supplied; no gate is certified as passed. This document is not approval, an executable amendment, a scientific amendment or a follow-up proposal. It requests no human ratification and authorizes no patient execution or remote write. All scientific interpretation remains exploratory.

## 1. Exact identity and review gate

Preserve P001 v1.1 and its original experiment pins. Before any real payload access, the campaign requires an agent-attributed decision binding the exact specification bytes and opposing-family review of both specification and executable implementation. The supplied specification says review is pending. The runner calls `verify_decision` with the campaign, specification, decision, review and runner paths, but that verifier and the decision/review records are not supplied. Its presence is not evidence of successful review or correct verification.

A future return must establish the actual specification/code/review identities and their valid decision bindings. The runner's checkpoint binding records specification SHA-256, code SHA-256, cohort SHA-256, manifest Git blob and review SHA-256. No missing hash or review outcome can be invented. An amendment changes specification identity and invalidates old authorization; this discussion changes neither. Unavailable authentication, compute connection or review authority is a stopping condition under the campaign.

## 2. Frozen selection and compressed-input integrity gate

- Read only `case_id` from the contribution table pinned to SHA-256 `aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9`; discard other columns, sort lexically and require exactly 99 unique eligible IDs. Cohort reuse does not permit outcome rankings as features.
- Require manifest Git blob `edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2`. For each eligible ID, select exactly one full-path admission `ses-01` NCCT-space Tmax derivative and one canonical `ses-02` NCCT-space lesion derivative. Missing or ambiguous selection fails; outcome content cannot resolve it.
- Extract only these 198 members. Do not stage noncanonical duplicate lesions, perform whole-archive extraction or access reserved cases. Preserve the supplied frozen membership; the campaign's reserved-case count and the specification's released-dataset count are not grounds to infer or revise membership.
- If using `train.7z`, verify exactly 99,014,629,647 bytes and MD5 `36ae28b9a17f7340b8bbef62b595cb57` before extraction. Verify each selected compressed member's recorded size and CRC32 before image opening, including reused staging or pre-staged inputs. Retain the selected-input SHA-256 bindings privately. Paths must remain within the private data root and satisfy the runner's symlink checks.

Selection-only preflight is not payload verification or evidence of a completed experiment. Label-byte integrity checks precede image evaluation; label image content may be opened for evaluation only after the corresponding prediction has been written.

## 3. Prediction, geometry and metric gate

Prediction uses only admission NCCT-space Tmax available by admission CT completion, on the full released Tmax grid. Every Tmax voxel, including background, must be finite and the array must be 3D. Any NaN or infinity stops the run. The prediction is strictly `Tmax > 6.0` seconds, without fitting, imputation, erosion, component filtering or lesion-dependent masking. The seconds convention remains an inherited metadata assumption and must be reported; an implementation check cannot establish empirical units from unavailable data. No follow-up intensities, outcome-derived features, post-treatment information or contribution ranks may enter prediction.

After the prediction is persisted, require a finite 3D label containing only `{0,1}`, matching shape and affine with absolute tolerance `1e-5` and relative tolerance `0`, and finite positive voxel volume. Geometry disagreement stops the run; no implicit resampling or additional case exclusion is allowed.

Completion requires all 99 patients, evaluated once with equal patient weight. The primary metric is arithmetic mean per-patient volumetric Dice: both masks empty gives 1, exactly one empty gives 0. Secondary metrics are median Dice, mean absolute lesion-volume error in mL and mean signed prediction-minus-label volume error in mL. Uncertainty is exactly 2,000 patient bootstrap resamples, seed `20260905`, with the central percentile 95% interval for mean Dice. No significance-based headline selection is permitted.

## 4. Execution, stopping and resume gate

The fixed budget is one CPU Colab run, at most 60 analysis minutes, with archive verification/extraction separately receipted and at most one staging invocation per new output path. No GPU, training, paid provisioning or hyperparameter search is allowed. Preserve the campaign's manual Run All arrangement; this document performs no execution.

Input integrity, scope, geometry, unit implementation or output identity failure stops the run. Retain the original console, completed patient checkpoints and attempt/failure records. An incomplete or failed run is not a negative scientific result, and scientific claims stop until invalid runs are resolved.

Resume may reuse only byte-verified checkpoints with identical specification/code/input bindings. The supplied runner additionally compares review/cohort/manifest bindings, verifies checkpoint bytes against its index, and checks input and prediction SHA-256 identities. A stale binding cannot be silently accepted. A new output path does not by itself authorize another experiment or altered specification.

## 5. Result-return and privacy gate

A future aggregate return must contain all five required and allowed publication files: `summary.json`, `resolved_config.json`, `environment.json`, `execution_receipt.json` and `RESULT_CARD.md`. Verify their mutual consistency with the exact reviewed implementation and private audit evidence. A completion status string or declared zero reserved-case access alone does not establish compliance. Require exactly 99 valid patient contributions and the pinned metric/bootstrap definitions before accepting a completion claim.

The configuration must retain the identity bindings, baseline, timing, seed and resample count. The environment and execution receipt must support the actual execution, including durations, staging versus analysis, resumes, failures, machine/agent identity and available usage as required by the campaign. Missing measurements remain null, never invented. The supplied runner records Python/NumPy/nibabel versions and timing, but does not itself provide every campaign provenance field. Its GPU measurement is null and explicitly uninstrumented; that is not proof of CPU-only execution. Missing compliance evidence leaves the relevant gate unresolved.

The result card must report the question, baseline/change, input timing, result and uncertainty, limitations, artifact references and next decision. For this discussion, interpretation remains pending verification; no follow-up is proposed. Retain failed-attempt cards and receipts without converting them into scientific findings.

Per-case predictions and metrics remain private on Drive. Patient IDs/paths, the private manifest, masks, staged inputs and per-case metrics must not enter the publication bundle. Supply the reviewed original console separately for audit. Any eventual publication also requires checked artifacts and outgoing-history inspection under campaign restrictions; returning evidence does not authorize a remote write. No such write is performed or proposed here.

## Interpretation boundary

Only after all applicable gates pass could a return describe this fixed threshold's performance against the released binary MRI-derived follow-up infarct mask in NCCT space after observed treatment. No result currently exists. The target is a surrogate measured days later, not histological truth or untreated counterfactual infarct. Reused development outcomes, selected membership, treatment/reperfusion, scanner/site differences, registration and inherited units constrain interpretation. The bootstrap interval describes within-cohort resampling variability, not external validation, causal uncertainty or correction for prior outcome use. No biological mechanism, model-use or clinical-deployment conclusion is licensed. These gates preserve the existing experiment; unresolved evidence is left unresolved rather than treated as approval.
