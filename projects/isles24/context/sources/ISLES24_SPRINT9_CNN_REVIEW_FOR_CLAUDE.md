# Sprint 9 CNN notebook: review and parallel-run recommendation

Date: 22 September 2026  
Notebook: `isles24_sprint9_unet_rotated.ipynb`  
Companion: `SPRINT9_UNET_NOTES.md`

## Recommendation

**Run the default `SMOKE=True` check in a separate GPU runtime while Sprint 8 continues. Before committing to the full paired experiment, correct the reference-linking and recovery paths described below.**

The core scientific design is reasonable for this week's comparison. The main defects are in how the notebook consumes a still-running Sprint 8 experiment and reuses its own saved predictions. They can cause missing comparisons, comparison against the wrong saved tree run, or unnecessary CNN retraining. The requested corrections do not require a new architecture or a different cross-validation protocol.

If CNN training has already begun, preserve its scores and checkpoints. No finding here establishes that a fresh, otherwise successful CNN fit is invalid. A corrected postprocessing path should reuse valid predictions.

## What this experiment can answer

It compares a small 3-D U-Net with Sprint 8's imaging-based tree reference D on the same 99 development patients and the same patient splits. Both use the 20 engineered cached imaging features without slice position; the CNN additionally receives a support-mask channel. These inputs include the supplied artery annotation where used by the cached features.

It asks whether learned spatial processing improves predictions over the tree pipeline on this representation. **It does not yet test demographic or treatment information in the CNN:** there are no CNN age, sex, admission-NIHSS or mTICI inputs. That is an appropriate scope for an initial CNN comparison, but it should be explicit in the meeting.

| Arm | How it selects the amount | How it selects locations | Meaning |
|---|---|---|---|
| `U_own_raw` | Sum of the CNN scores, converted to a voxel count | Highest raw CNN scores | CNN's own amount and ranking |
| `U_own_smoothed` | Same amount as `U_own_raw` | Highest smoothed CNN scores | Effect of smoothing the CNN ranking |
| `U_Dvolume_smoothed` | Sprint 8 D's predicted volume for the same patient/fold/seed | Highest smoothed CNN scores | CNN placement using D's amount |
| Sprint 8 D | D's predicted volume | D's smoothed tree ranking | Tree reference |

For the last CNN arm, the “same amount” comes from another model's prediction, not from ground-truth lesion size. Once the reference grid and observations are verified, comparing it with D holds the predicted voxel count fixed and tests placement. The CNN is not being given the answer key.

Both models remain restricted to the cached feature mask. This CNN cannot recover lesions outside that mask merely by learning a spatial representation. Full lesion truth is appropriately retained for scoring.

## Verified strengths and limits of this review

Cell references count **all cells, starting at 1**, including Markdown.

- The outer-fold and inner-partition construction matches Sprint 8 R3. Patient partitions depend on shuffle/fold, not training seed.
- Training statistics and robust scaling use only the relevant training subset. Epoch selection and smoothing use inner validation; outer held-out outcomes are not used for those choices.
- The default 48×48×32 patches are compatible with the two pooling levels. The architecture has 348,529 parameters, consistent with the notes' approximate count.
- The six core Torch definitions match the historical Sprint 5 R1 implementation by parsed-code comparison. That earlier notebook's cell 13 contains saved GPU training output. This supports the inherited core; it does not establish that the new Sprint 9 wrapper has executed successfully.
- Actual execution paths read Sprint 8 files and shared caches; trained scores, checkpoints, masks and reports write to the separate Sprint 9 output root. No call that rewrites Sprint 8 outputs was found.
- All nine outer code cells parse as Python. The supplied notebook has no saved execution outputs. Torch was unavailable in the review environment, so no new CPU/GPU network step or patient training was run here. Focused non-Torch probes were used for the identified data-link and validation issues.

Input identities:

| File | SHA256 |
|---|---|
| Sprint 9 notebook | `f5aa4ee351e8b2bb81810565becca789d7bf0f7003934bd0df588f859f14ddea` |
| Sprint 9 notes | `c726ec034c296f893f03b1007b9e6a1bc5435350ba38fe7791f0fe4b755d7b4b` |

## S9-01 — Pin and validate the exact Sprint 8 reference

**Priority: before relying on paired results. Cells 7 and 15.**

With `SPRINT8_RUN=None`, the notebook chooses the newest directory whose held-out and inner-validation lists match. Older revisions can have those same lists. The link does not verify the Sprint 8 run manifest/fingerprint, identical cache contents, complete training/partition membership, or the validity of the D CSVs being imported.

The D import reads matching rows without checking complete fold coverage, duplicate keys, finite values or row fingerprints. The tree-map reader checks shuffle/seed but not the linked run fingerprint, fold, recipe or full grid identity. Sprint 9's saved derived results do not record the Sprint 8 reference identity in a way that prevents reuse after the reference changes.

**Requested correction:**

1. Pin the current Sprint 8 R3 run explicitly using its printed `run-...` directory. Preserve that exact reference in the Sprint 9 comparison metadata.
2. Check the full relevant partition membership, case set, cache-content identity and grid against the Sprint 8 manifest. For smoke mode, validate the requested subset of the full Sprint 8 protocol.
3. Import only complete, valid D observations with matching source-run fingerprints and unique `(shuffle, fold, train_seed, case)` keys. Validate finite predicted volumes and the relevant metrics.
4. Bind each derived D-volume result and comparison to the particular D artifact used. Check the corresponding tree mask identity before displaying it.

Keep the CNN training identity independent of later D availability. Changing the comparison reference should invalidate/recompute the dependent comparisons, not automatically require fitting the CNN again.

## S9-02 — Make later tree results usable without repeating CNN training

**Priority: before the full simultaneous run. Cells 7, 9, 11 and 13.**

`S8_FOLDS` is populated only once during setup. If Sprint 8 is still running, later completed folds never enter this dictionary. Rerunning only the summary cell does not refresh it.

There is also a costly recovery problem. `run_fold` expects two own-volume arms when D is absent and three arms when D is available. A valid saved two-arm fold fails that exact recipe-set check after D arrives. The function then goes through both inner and final CNN training, even though the notebook already saved the raw CNN scores, chosen width and chosen epoch. There is no path that loads those valid scores to generate only the newly available comparisons.

A small probe confirmed that a valid two-arm fold becomes invalid when the third arm is added to the expected recipe list. This is a real consequence of the current implementation, not a hypothetical increase in model complexity.

**Requested correction:** separate the work into two reusable operations:

1. **Train and predict once:** produce validated raw CNN scores with the selected width/epoch and record training completion.
2. **Score, compare and draw:** load those scores; create own-volume masks/metrics and, when valid D observations arrive, create D-volume masks/metrics and comparisons.

Add a read-only reference refresh before the second operation. Re-running it should use saved CNN scores and should not call `train`. It should also repair missing derived CSVs or masks without refitting when the underlying scores remain valid.

Report two completion states: **CNN predictions complete** and **tree-dependent comparisons complete/pending**. At present, “all planned combinations complete” can describe a run with no D-volume arms at all because absent references shrink the required recipe list.

This is the principal change that makes the proposed simultaneous workflow efficient.

## S9-03 — Make checkpoint identity and stopped-training recovery stable

**Priority: before trusting automatic resume for the full run. Cells 7 and 11.**

`CODE_DIGEST` hashes `In[1:]`, the notebook's execution history. Repeating setup in the same kernel can change the run directory even if the intended experiment has not changed. At initial setup, this history also excludes the later, not-yet-executed training and scoring cells. The notes' promise that a dead runtime simply requires Run All is therefore too strong.

Use a stable identity derived from the relevant notebook/code contents and scientific configuration, with an explicit way to resume the existing validated run. Preserve old directories and do not silently relabel them. Keep smoke and full runs distinct.

The checkpoint saves model, optimizer, AMP scaler, NumPy sampling state, curve and early-stopping state, which is useful. However, after loading an inner checkpoint with `wait >= patience`, `train()` still enters the epoch loop. Record that the inner training already completed/stopped, or check that condition before another epoch. Restore its preserved best model and selected epoch without further training.

Combine this correction with S9-02: a fully saved prediction artifact should take precedence over reconstructing an entire training operation merely to regenerate reports.

## S9-04 — Preserve valid undefined metrics and restore complete reporting

**Priority: small scoring fixes before full reporting; the validation issue can also stop a fold. Cells 7, 9 and 13.**

### Feature-mask AUROC/AP edge case

The scorer returns NaN when the truth inside the feature mask has only one class. The validator permits that NaN only when the entire lesion truth is empty. A real lesion entirely outside the feature mask therefore produces a legitimate undefined ranking metric, but `fold_valid` rejects the fold. This is the same issue identified in Sprint 8 R3.

An extracted-function probe reproduced the refusal. It does not establish that one of the current 99 cases triggers it.

Store the in-mask positive/negative counts, or validate against the unchanged cache, and permit undefined values under the metric's actual domain condition. Keep complete ground truth for Dice/recall/volume scores. Do not replace undefined values with zero or crop the truth to make validation pass. Already-saved valid predictions should be rescored/revalidated without fitting again.

### Missing tree truth in the volume export

The D import does not carry `lesion_ml`. Consequently the concatenated D rows have missing truth values, and `volume_pred_vs_true.csv` exports `true_ml=NaN` for them. This was reproduced with the imported row structure.

Import and verify the true volume against the identical current cache, or derive it consistently from that verified cache for both models. This is a reporting correction, not a reason to retrain.

### Summary coverage

The notebook calculates precision, recall, lesion-count difference, ASD and feature-mask AUROC/AP per patient, but the main summary omits them. In particular, lesion-count difference is missing despite the intended comparison with Sprint 8's metric package.

Export the existing measures with their valid patient/observation counts. Retain Dice/voxel F1 and lesion-wise F1 as separate concepts. Descriptive tables can have different numbers of completed observations while the jobs run; comparative claims should use the explicitly matched contrasts and their counts.

Some figure strings contain a literal `\\n` rather than a newline escape. Correct those before producing the meeting figures; this is a presentation-only change.

## Concurrent execution and practical launch steps

The source separates output roots:

| Data/output | Sprint 9 access |
|---|---|
| Shared feature caches | Read |
| Sprint 8 partitions, D CSVs and masks | Read |
| `sprint9-unet-PRIVATE` scores/checkpoints/figures | Write |

Use a **separate GPU-backed Colab runtime**, with `torch` reporting `cuda`. Avoid sharing the running Sprint 8 Python kernel: both notebooks define overlapping global names such as `CACHE`, `RUN_DIR` and `FINGERPRINT`.

Colab does not guarantee fixed GPU availability or runtime limits, including for paid plans; a second simultaneous GPU runtime depends on current allocation. Its official FAQ also identifies Drive operation/bandwidth quotas. Separate output directories prevent direct result overwrites, but both notebooks still consume the account's compute and shared-storage resources. See [Google's Colab FAQ](https://research.google.com/colaboratory/faq.html), sections “Resource Limits” and “Why do Drive operations sometimes fail due to quota?”

Recommended sequence:

1. Leave the ongoing Sprint 8 run intact.
2. Open Sprint 9 in a separate GPU runtime and keep `SMOKE=True` for the first check. Explicitly identify the intended Sprint 8 run if its folder is available.
3. Confirm the configured-shape Torch step, the one-fold inner/final training, saved predictions, metric validation and example figures. A smoke result is a timing/memory/execution check, not a scientific performance estimate.
4. Have Claude correct S9-01 through S9-04, especially adding a no-training postprocessing path. Preserve any valid smoke artifacts.
5. Run the full two-shuffle/two-seed protocol under its own stable identity, refreshing validated Sprint 8 references as needed. Keep the 25 final-evaluation and 24 reserve patients untouched.

There are 20 full-run fold/seed combinations and two training phases per combination. Their duration depends on selected epochs, full-volume validation/inference and the allocated hardware. Use this notebook's measured timing; the old roughly 12-minute figure included earlier Sprint 5 notebook stages. That historical run logged about 3.8 minutes for inner training and about 3.9 GB for 69 dense volumes, which is evidence of feasibility on that prior runtime, not a guarantee for the current one.

The smoke fold still builds the full outer-training subset's dense feature volumes, so it usefully tests host RAM as well as GPU memory. All 99 caches are also held in memory. A successful tiny Torch step alone does not establish that the complete fold fits.

## Interpretation for the meeting

Keep four questions separate:

- Does smoothing improve the CNN's own predictions?
- Does the CNN with its own score-derived amount outperform D overall?
- With exactly D's predicted amount, does the CNN place that tissue more accurately?
- Does using D's amount improve the CNN compared with its own amount estimate?

Lesion-centred patch sampling and the Dice/BCE training loss do not establish probability calibration. Treat the CNN's score sum as its volume-estimation rule. The matched-D-volume arm helps distinguish a ranking problem from an amount-estimation problem.

This is development evidence on patients used throughout model development. Two seeds provide a useful sensitivity check; they do not give a precise estimate of all training variability. A result here evaluates this compact CNN recipe, not CNNs as a whole or the challenge-winning nnU-Net pipeline.

## Requested response from Claude

Return a focused revision of the Sprint 9 notebook and notes. Preserve the architecture, patient partitions and planned contrasts. Demonstrate that a completed CNN fold can acquire newly available D-volume comparisons **without another training call**, that a mismatched reference is refused, and that setup/recovery finds the intended existing run. Correct the metric/export issues with small fixtures.

No new patient experiment is needed to verify those software changes. The next real-data work should be the smoke check and then the planned full experiment, with Sprint 8 results and completed CNN predictions preserved.
