**Sprint9 r4 readiness review, with Sprint10 compatibility findings**

Reviewed 22 September 2026. Recommendation: run the supplied Sprint9 smoke test on a separate GPU runtime. If it completes all four intended arms with usable saved outputs and acceptable memory/time, proceeding to the full protocol is reasonable. No concrete default-path CNN training blocker was found. Better design does not yet establish better predictive performance.

The uploaded notebooks contain no execution outputs. This review inspected source and ran targeted synthetic checks; it did not train a network, load the private patient caches, or measure GPU performance. PyTorch is unavailable in the review environment. Claude's reported stubbed checks are not treated as real Torch execution.

**Files reviewed**

| File | SHA256 |
| --- | --- |
| isles24_sprint9_unet_clinical.ipynb | `2253236c2226ea0cf9e9e77d5ebfb2fd3b641f51c01e778d6426657c34011e27` |
| isles24_sprint10_compare_trees_vs_unet.ipynb | `f13ac78f6a47c2b638850af89a5198b3a6d5ff9a29f2e62c6638ef8244abce3f` |

Also read SPRINT9_R4_AND_SPRINT10_NOTES.md, compared the previous isles24_sprint9_unet_rotated.ipynb, and checked compatibility with the current Sprint8 r4. The two notebook hashes match the notes. Cell numbers below count all cells, including Markdown, starting at 1.

**What improved and what was verified**

| Previous concern | Current implementation and evidence |
| --- | --- |
| CNN training depended on a changing Sprint8 output directory | Sprint9 no longer reads Sprint8. Cross-run comparisons are in Sprint10. Current code preserves the same outer, inner and volume-fold partition construction. An extracted-code fixture reproduced identical partitions for all ten shuffle/fold combinations. |
| Later comparisons or missing outputs could trigger CNN retraining | Cells 11/13 separate `train_predict` from `postprocess`. A fixture using the actual functions saved two patients' raw predictions, generated both recipes and masks, deleted the CSV and one mask, then regenerated them with training and preparation replaced by functions that would fail if called. Neither was called; the saved raw-score hash stayed unchanged. |
| No demographics or treatment-related inputs | Four arms now compare imaging alone, broadcast baseline clinical inputs, FiLM baseline conditioning, and broadcast post-intervention information. |
| Potential leakage through preprocessing | Clinical means/std and imaging preprocessing are fitted on inner-training patients during selection and outer-training patients during final fitting. A synthetic held-out clinical perturbation did not change fitted statistics. No new outcome leakage was found. |
| Stopped checkpoints could resume for extra epochs | Cell 13 now returns immediately when a loaded checkpoint already reached early stopping or its requested epoch count. Model, optimizer, scaler, patch-sampling RNG and early-stopping state are restored. |
| Undefined mask ranking scores crashed validation | The one-class mask condition is present, with explicit positive/negative counts. Full-truth segmentation metrics still include lesions outside the feature mask. |
| Incomplete metrics and maps | Sprint9 exports Dice/voxel F1, lesion F1, precision/recall, volume errors, lesion-count error, ASD and mask ranking metrics, with valid counts for several potentially undefined measures. Maps include ground truth and TP/FP/FN overlays. |

All ten Sprint9 code cells and all eight Sprint10 code cells parse. FiLM's encoder/decoder channel widths and scale/shift broadcasting are consistent on inspection. NumPy fixtures verified clinical channel insertion, the support mask remaining last, conditioning dimensions, padding and overlapping-window coverage. These checks do not replace the configured Torch smoke run.

**What the clinical arms actually test**

| Arm | Inputs beyond the 20 cached imaging features and support mask | Default full-protocol runs |
| --- | --- | ---: |
| U_base | None | 20 |
| U_bc_baseclin | Age, sex and admission NIHSS, each with a missing indicator, broadcast as extra image channels | 10 |
| U_film_baseclin | The same baseline vector controls feature-channel scales and shifts inside the network | 10 |
| U_bc_postint | Achieved reperfusion grade and its recorded indicator, with the vector's missing indicators | 10 |

These field counts assume the same available data as the user's recent Sprint8 output. Onset-to-imaging time and explicit IVT/EVT flags were absent in that output. With three baseline fields, broadcast has **27 input channels** (20 imaging + 6 clinical/missing + 1 support), and FiLM has **21 image/support channels plus a six-value conditioning vector**. Post-intervention broadcast has 25 channels. The notes' baseline counts of 29 channels/eight conditioning values do not describe these actual available fields; they would require four usable baseline fields.

The post-intervention arm conditions on achieved reperfusion information. It is not a treatment-plan recommendation or evidence of what would happen to the same patient under a different treatment. The previously observed 68 recorded grades, mostly 2c/3, and 31 missing grades limit interpretation. Missingness may carry documentation/site information. No additional treatment feature should be guessed from its absence.

Clinical-versus-baseline contrasts correctly match shuffle, fold, seed and patient before averaging within patient. Thus the extra baseline seed does not contaminate the matched clinical comparison. Clinical arms have only seed 1: useful exploratory evidence, but not a demonstration of clinical gains across training seeds.

**Correct the workload estimate before planning the full run**

The notes undercount the workload by a factor of two. The actual defaults use two shuffles:

- Baseline: 2 shuffles × 5 folds × 2 seeds = 20 combinations.
- Each of three clinical arms: 2 shuffles × 5 folds × 1 seed = 10 combinations.
- Total: **50 arm/fold/seed combinations, each with an inner and final training = 100 training runs**, plus validation, inference, preprocessing and exports.

The supplied `SMOKE = True` schedules one fold/seed for each of four arms: eight short inner/final trainings, with the inner runs capped at two epochs. A final fit may use one or two selected epochs. This smoke result is a runtime check, not the full research result. Do not multiply its total minutes by a simple fixed factor and call that a reliable full-run estimate: full inner fits allow up to 60 epochs, and validation/inference add overhead.

**Run recommendation**

1. Start the new Sprint9 in a separate GPU runtime, using its supplied `SMOKE = True` and `RUN_ID_OVERRIDE = None`. Sprint8 can continue independently; Sprint9 only shares the cached inputs and phenotype files.
2. Confirm that the logs activate all four intended arms and recover the expected clinical fields. If only the imaging baseline runs because clinical files were not found, that is not a successful clinical experiment.
3. Let the smoke run exercise actual training, inference, saved raw scores, metric tables and example maps. Check finite losses and the reported memory/time. The early base/FiLM preflight alone is not the complete smoke run.
4. If this completes normally, set `SMOKE = False` and Run All from the top. Leave `RUN_ID_OVERRIDE = None`; the full protocol gets a separate identity and does not reuse the smoke results as research results.
5. Use matched within-run clinical contrasts for the meeting. Sprint10 can be corrected separately and run later from the saved predictions. Its remaining problems do not require delaying the Sprint9 smoke test or retraining the CNN.

No need to add more arms or new infrastructure before obtaining this runtime evidence.

**Targeted Sprint9 follow-ups**

| Priority/timing | Location | Finding and suggested correction |
| --- | --- | --- |
| Before using a manual continuation override across revisions/environments | Cell 9 | `scientific()` excludes code version/digest and dependency versions. A manual override could accept a changed numerical environment while retaining the old manifest. Record the current code and dependencies per execution, and require matching effective dependencies or an explicit compatibility decision. A manual version label is not a source-content hash. Default fresh runs with override unset are not blocked by this. |
| If clinical mapping counts differ, or before reusing the parser on other files | Cell 7 | Alias merging detects typed conflicts but subsequently chooses `raw[0]`. A first unparseable alias can hide a later valid alias: a fixture with `not recorded?` followed by `3.0` lost the valid mTICI grade. Select the unique valid typed value or the corresponding successfully parsed raw value; preserve failed-parse provenance separately. Current incidence is unknown without the private files. |
| Before enabling the extended-baseline option | Cells 2/7/9 | `RUN_EXTENDED_BASELINE=True` parses extra fields but creates no extended group/arm consumed by Sprint9. Implement the arm or remove the misleading option/comment. It is false by default. |
| If host RAM is tight | Cell 13, `train_predict` | The final training volumes remain allocated during held-out inference. Clear `Pf['vols']`, labels and centres once final fitting ends, retaining the preprocessing closures and conditioning needed for held-out prediction. This avoids a preventable memory peak; no measured out-of-memory failure is claimed. |
| Before relying on repaired/copied artifacts | Cell 11 | Strengthen score validation with required `best_epoch`, allowed probability range and explicit shuffle/fold/seed metadata. Reject infinity in conditional metric columns separately from allowed NaN. Existing atomic saves and current filenames are consistent; these are robustness improvements rather than demonstrated normal-run failures. |

The FiLM preflight could also check finite gradients and conditioned inference explicitly, as the base preflight does. The full all-arm smoke run already exercises the actual fusion/inference paths, so this is not a reason to demand another design revision first.

**Sprint10: fix before interpreting its comparisons; no Sprint9 retraining required**

Sprint10 is a postprocessing notebook. It reads saved tree/CNN results and creates matched-amount predictions: use the CNN's spatial ranking but select the amount predicted by tree D. This asks whether placement differs when the predicted lesion amount is held equal. It does not use the ground-truth lesion amount to make those predictions.

The current default notebooks agree on patient partitions, filenames, metric schema, score format and mask format. Four consumer-side issues remain:

1. **Cell 8 bypasses robust score validation.** Its matched-amount loader checks fingerprint/arm but not the full declared case set, allowed smoothing width, raw array shape or finite probabilities. Synthetic fixtures accepted an invalid width and incorrect declared cases; all-NaN scores in the outside-mask lesion case still produced a finite Dice row. A corrupt archive aborts the cell. Reuse/extend Sprint9's score validator, verify the exact requested partition and seed, and report invalid files without using them. Do this before interpreting matched-amount results.
2. **Cell 5 overstates partition checking.** It checks outer train, held and inner-validation lists, but not `inner_train`, `vol_folds`, or extra partition keys. Compare the complete dictionaries. Check parsed clinical table identity and field sets before describing tree/CNN clinical inputs as identical. The current sources generate matching partitions; this is protection against comparing changed runs.
3. **Cell 10 completion reporting can hide missing work.** It summarizes groups that were imported, so entirely absent combinations disappear. Enumerate expected combinations from both manifests and show complete, pending, invalid and paired states. Keep interim comparisons explicitly provisional.
4. **Reporting/validation needs finishing.** Cell 6 permits infinity in conditional metric columns; reject it. Several metrics remain in the data but are omitted from the comparison summary. Carry precision, recall, specificity, AUROC/AP and empty-prediction rate with valid counts into the useful comparison exports.

Set Sprint10's placeholder `SPRINT9_RUN_DIR` to the completed or progressing **full-protocol** directory, not the smoke directory. Its existing smoke exclusion is appropriate. Do not change Sprint9's output format solely to solve these Sprint10 loader/reporting issues.

**Literature and interpretation corrections**

Clinical conditioning has relevant published precedent. Pinto et al. used TICI information for ISLES2017 outcome prediction, including an extra channel **before the final layer** and a custom TICI-related loss. Therefore, describing Sprint9's input-level broadcast as exactly their early-fusion implementation is inaccurate. Call it a related adaptation. Their MRI dataset, architecture and training objective differ from this cached CT-feature pipeline.

Lemay et al. studied FiLM conditioning for segmentation and reported a 5.1% average Dice increase using tumour-type information for spinal-cord tumour segmentation. This supports FiLM as a reasonable mechanism to test; it is not an expected effect size for stroke demographics or this small cohort.

Sources checked:

- Pinto et al. (2018), *Stroke Lesion Outcome Prediction Based on MRI Imaging Combined With Clinical Information*: https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2018.01060/full (especially section 2.3.2).
- Lemay et al. (2021), *Benefits of Linear Conditioning for Segmentation using Metadata*: https://proceedings.mlr.press/v143/lemay21a.html.

Keep the existing disclosure that both pipelines use cached, partly annotation-assisted features and mask-constrained predictions. A CNN-versus-tree difference compares complete pipelines: architecture, loss, sampling and preprocessing also differ. It does not isolate spatial context alone. Neither adding clinical channels nor FiLM expands predictions outside the feature mask. The planned matched-amount comparison helps separate amount from placement, while full-ground-truth Dice/F1 and missed-lesion measures retain the consequences of mask exclusions.

**Practical conclusion:** this revision resolves the previous coupling and retraining concerns substantially and adds meaningful clinical comparisons. Run its existing all-arm smoke test now; use its actual outputs to decide the full run. Correct the notes' workload and channel counts, and fix Sprint10's reader before trusting cross-run comparisons. These follow-ups do not justify restarting an otherwise successful Sprint9 training run.
