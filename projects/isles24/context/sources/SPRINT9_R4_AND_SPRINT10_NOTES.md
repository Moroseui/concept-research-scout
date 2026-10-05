# Sprint 9 r4 (independent U-Net with clinical fusion) and sprint 10 (comparison of finished runs)

`isles24_sprint9_unet_clinical.ipynb` (SHA256 2253236c2226ea0cf9e9e77d5ebfb2fd3b641f51c01e778d6426657c34011e27) · `isles24_sprint10_compare_trees_vs_unet.ipynb` (SHA256 f13ac78f6a47c2b638850af89a5198b3a6d5ff9a29f2e62c6638ef8244abce3f) · 22 September 2026

## Why the design changed after the CNN review

The review's largest items (S9-01 pinning a live sprint 8 run, S9-02 acquiring tree comparisons later without retraining) both came from one design choice: the training notebook read another notebook's outputs. Partho's question ("why read sprint 8 at all?") is the right one. In r4 the training notebook reads nothing from sprint 8; it only derives the same partitions from the same seeds and saves every arm's raw scores. All cross-run work (matched-amount arms, contrasts, side-by-side maps) moved to sprint 10, a no-training notebook that reads two finished or in-progress run directories and refuses to compare them unless caches, cases, grid and partitions are identical. That dissolves S9-01 and S9-02 rather than patching them.

Items kept from the review: stable code identity with a continuation switch and a stopped-training resume (S9-03); the one-class mask rule for undefined ranking scores, true volumes on every row, the full metric set with valid counts, and real newlines in figures (S9-04).

## Clinical information in the network (new)

The review noted the CNN had no demographic or treatment inputs. The literature offers three families of fusion, and r4 implements the two that fit this architecture:

- **Broadcast (early fusion).** Each standardized clinical value and a missing indicator are tiled as constant channels inside the support mask. This is how Pinto et al. (2018) fed each patient's TICI score to a CNN for ISLES 2017 lesion outcome prediction, and it is the direct counterpart of sprint 8's arms F and G, so the tree and the network can be compared on the same fusion mechanism.
- **FiLM (feature-wise linear modulation).** A small generator maps the clinical vector to a per-channel scale and shift applied after every convolutional block, initialized to the identity so the network starts as the base network. Lemay et al. (2021) adapted FiLM to segmentation and reported an average Dice gain of 5.1 percent when conditioning on tumour type, with mixed results reported by others on U-Nets; it is the cheapest intermediate-fusion mechanism.
- **Late fusion** (a separate patient-level model adjusting the amount) already exists as sprint 8's K, I and J and can be applied to any saved network scores later.

Arms: `U_base` (no clinical; seeds 1 and 2), `U_bc_baseclin` (broadcast: age, sex, admission NIHSS), `U_film_baseclin` (FiLM: same fields), `U_bc_postint` (broadcast: reperfusion grade and its recorded indicator). Clinical arms run for seed 1 by default; each arm has a raw and a smoothed recipe with the amount from its own score sum. Fields are read with sprint 8's manifest and parsers; standardization and missing-value handling use training-fold statistics only; the parsed clinical table's digest is part of the run identity. Post-intervention arms are conditional-on-treatment predictions, and the cohort has no reperfusion failures, so that signal is thin (as in sprint 8).

## Running

1. Sprint 9: separate GPU runtime. `SMOKE = True` first (one fold, seed 1, 2 epochs, all four arms): it exercises both fusion paths and prints minutes, host RAM and peak GPU per arm. Then `SMOKE = False`, Run All. The full protocol is 10 fold-and-seed combinations for `U_base` plus 5 (seed 1) for each of the three clinical arms, two trainings each; use the smoke timing to plan. Interrupted trainings resume from their last epoch; valid score files are never retrained.
2. Sprint 10: once both runs have folds, set `SPRINT9_RUN_DIR` to the printed sprint 9 directory (not the `-SMOKE` one) and run; re-run any time to pick up newly completed folds. Outputs: `completion.csv`, `summary_by_recipe.csv`, `paired_contrasts.csv`, `comparison_reference.json`, `figures/example_maps_trees_vs_unet.png`.

## Offline verification (synthetic fixture, torch stubbed, no training)

Sprint 9 r4: clinical mapping and arm activation; broadcast volumes carry 20 + 8 + 1 channels for the baseline group and 20 + 4 + 1 for post-intervention; the FiLM arm passes an 8-value conditioning vector; with `train()` replaced by a function that raises, fake valid score files produced every arm's fold files, the summary and the maps. Sprint 10: refuses runs with different partitions (tested earlier on r3's checker, same code), imports both runs' validated folds, builds the matched-amount arms from saved scores, computes the contrasts and draws the combined map. The torch training code (sprint 5's, plus the FiLM wrapper) has not executed here; the SMOKE fold is its first run.

## Interpretation rules

Development evidence on the 99; the 25 remain unscored. Two seeds give observed sensitivity, not a variance estimate. The U-Net and the tree share the same cached representation (including the annotation-assisted features), so this compares learned spatial processing with the tree recipe, not a source-image network. A clinical gain in the network counts only against `U_base` on matched fold and seed; a gain over D alone does not distinguish architecture from information.
