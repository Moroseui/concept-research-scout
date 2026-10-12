# Independently reviewed Idea2 interpretation

# Summary

Does fusion help by placing predicted tissue better, estimating its amount better, or both? Across 99 exposed development patients, fusion improved placement over tree ranking at every fixed amount. At fusion ranking, replacing tree amount with nnU-Net amount reduced mean Dice by 0.0366 (95% interval −0.0555 to −0.0174). Fusion amount changed Dice by only +0.0023 (−0.0061 to +0.0108), while reducing mean absolute volume error by 4.31 ml. Mean Dice with fusion ranking and fusion amount was 0.2491; below 5 ml true infarct volume it was only 0.0611. All 891 allocations were feasible. These saved-fit diagnostics do not establish clinical benefit, anatomical explanations or untouched-test performance. Intervals exclude training and selection uncertainty; admission provenance remains unverified.

# Details

**Question and evidence scope.** The target is released follow-up infarct tissue predicted from information available by completion of admission CT. This fixed3×3 diagnostic asks how three frozen score rankings behave when given three saved predicted amounts. It analyzes existing split101/seed1 products on the same 99 development patients. It neither trains a predictor nor measures new-cohort performance. T denotes tree, N nnU-Net with CT/maps/CTA, and F the fixed half-sum fusion. A cell `ranking__amount` combines those two choices. Evidence keys F/C/A/I/L/V refer to the linked originals in the identity table; S/CODE and the other keys link to their inspected sources below. All numerical tables below transcribe existing aggregate statistics; brackets are the saved 95% intervals for patient means or paired mean differences. No patient payloads were used for this interpretation.

**Original result identities.** The six originals below were opened and their byte lengths and SHA256 checked. The five scientific products also match the per-file entries in validation.json; all six match the supplied execution intake receipt. These identifiers refer to the actual returned files, not the prior Sprint13A external archive.

| Original output | Bytes | SHA256 |
| --- | --- | --- |
| [amounts.json][A] | 16016 | `84993970fe8a99f53530e4804c3557e0ea2cbdb9f525ae69bd28d1f2b63dedc6` |
| [contrasts.json][C] | 303716 | `63b4e91fb6fec51493e832745fa50706b16ed2aa6076eeadb41fee9be2e024e6` |
| [factorial.json][F] | 128985 | `149725bb7277864c25b360185ca0d8306a82b72149ac51a1435720871df39582` |
| [integrity.json][I] | 1474 | `da29934de8b554337a6c41d7a883ac87d8ba1740093d085b75219be8f273d366` |
| [limitations.md][L] | 2389 | `1c988644eb94536c4838a164c01a33a0829ecf2543a91a75a3bd0cf7d7f0be89` |
| [validation.json][V] | 1725 | `ca49da2e80b2de14452c2dc8c61bd1c0d20f3eb199bc3d6e73eaa90cb10dd930` |

The original result directory is `current/runs/1ed7333ef01540157462eb45ff63c3023705b752a8243f91b3ee21c0b68ee4fa/results/idea2/`. The [supplied execution records](/workspace/prompt.md:710) identify run `diagnostics-b203ee1ce27e909d9d78d44a`: execution manifest SHA256 `a160fa5a001c45529a1d18269defc8e13cf42111280b49c1aab56a1f1abfd0ed`, intake receipt SHA256 `88677d2e8f6fb57f5f6d4414ffc567e0a54eda3f0c378a994ba50aa27f2f0568`, schema `idea2-private-aggregate-intake/v1`. Those records are supplied inline in prompt.md; their separately named current/ files are not mounted here. The receipt references underlying execution `eb1c97343317560537612ff5a37e4e21e0933f2c6caa3ef34a5c93ece9970b45`, exit `faa6993d06e5289e712cdfcd0a056246d1fdd9e832c9caf115653d64cd42dc60`, and controller validation `e6bd21e3baf3894c4fdb87cd299555288ddf0090d40df33422673a69019bcbd4`; those underlying originals are not separately available for inspection. The last hash is distinct from the returned scientific validation.json hash.

The [package manifest][P], SHA256 `830d9a6036cf20372470674081ae1d48a56941f219afe200b4fce98c879687c7`, and intake agree on program `a105d6c49110c2479ed2917eda2b82519db8d4a3c8618d5c22cc7ae4fa99ae99`, scientific review `7d5383067225794a661d86876ce082c00af0c9f8c7483b894350a2bfd02fed22` and implementation review `7bee839a180a6a63f039cb6b0e70f838dce0649709f76fbf64122858dd0ce3e6`. These are receipt bindings, not claims of inspecting those review originals. Validation binds the [frozen specification][S] `462d91cb9c351832cccc0b9c5f572a0b09e9e57a242b68ec163c52347ba507db`, [analysis source][CODE] `cea229e28e9905bf046a1c2054c3b74b17c8b2ed0f132e0018e77baa9e41e5d4`, execution selection `613bb59adc7836c8a4120e0ff9e6e2df5befe6d643bb263e0a86cc84dca228a5`, CPU source `5311301bdb5196fd21940f56b233f23967b6a734` and environment `0f71b0d0a8131090bca668b7da55e3aecf70392687b23dd7f7a264f0532fb34a`. The observed versions are Python 3.12, numpy 2.1.3, scipy 1.16.3 and nibabel 5.4.2.

**What establishes completion.** The supplied CPU execution manifest reports no training. The intake records 728 captured input files and four package files verified before and after execution, with incremental cost 0 micro-USD. Separately, the program reports 614 selected files verified, zero selected files missing, 99 geometry/cache checks, 198 reported-mask checks and 792 table comparisons. These counts concern different scopes, not a discrepancy. The native probability/segmentation minimum Dice is 1.0; maximum smoothing and table discrepancies are zero. All seven checks in validation.json are PASS, covering identity/environment, membership/files, saved geometry, factorial, paired and amount accounting, and aggregate return. There are 45 cell-group, 110 contrast-group and 15 source-amount-group denominator checks. No one of these arithmetic checks validates the original training, acquisition timing or biological interpretation. [I][I], [V][V]

No required fixed3×3 result is missing, and the supplied evidence supports a completed aggregate return. No failed or partial fixed3×3 patient attempt is reported in this packet. Real-run elapsed time, resource utilization, intervention time, token totals and total historical spending are not supplied; the zero incremental cost is not an estimate of those quantities. The [20-test synthetic PASS receipt][TEST], SHA256 `008be90a773f4dcbb0ae9a698c10415d31416af89a1d4a97688c5b95c496bf93`, explicitly has real_data_execution=false. Its 29.06 seconds are synthetic-test duration, not diagnostic runtime. Neither this synthetic receipt, a specification approval, file availability, nor the older SAVED_EVIDENCE_IDENTITY_ONLY records establish real execution; the current return is supported by the distinct bound intake and validated products.

The exact [first][FIND1] and [second][FIND2] finding records retain the earlier REVISE judgments: failed synthetic tests, environment mismatch, and inaccurate receipt-availability wording. Both are currently closed by the embedded closure `8b3ba0c8ae317fd7d4db8839cc3ddf16638aacc051df1a1d44880dc722cace6a`, whose embedded bytes were checked against that hash. The original failures remain failures of their historical versions; they are not negative scientific results. Closure concerned the prior v4 program and does not demonstrate this v5 execution. The current finding index contains no open blocker record. The five earlier diagnostics and their acceptance remain historical evidence; their full result bundle is not staged here, so no missing earlier statistic is reconstructed. [S][S], [L][L], [FIND1][FIND1], [FIND2][FIND2]

**Fixed definitions and uncertainty.** Tree amount is the voxel count in its saved smoothed mask. N amount is the count from native-threshold segmentation followed by nearest-neighbour resampling, not thresholding resampled probabilities and not their sum. F amount is the ties-to-even rounded full-grid sum of the float64 half-sum of raw tree and resampled N scores, with the original candidate-capacity cap. Counts are determined before smoothing and without truth.

All nine rankings use the same candidate domain: tissue support union voxels whose N probability is strictly greater than 10⁻⁴. Tree scores are zero outside tissue support. Each of T, N and F is smoothed with the saved tree fold width using normalized Gaussian smoothing within that domain: G(score × domain)/(G(domain)+10⁻⁶), sigma=width/2 voxels, reflect boundaries and truncate=4; zero width is identity with domain restriction. Ranking uses descending float32 processed score, then ascending flat C-order index to break ties. Exactly the amount-column count is selected. The grid is orthogonal 2 mm, 0.008 ml/voxel. Full lesion_full is scored, including truth outside the domain. Truth supplies evaluation and descriptive strata only. [S][S]; [CODE][CODE], frozen_predictions, smooth, metrics

The diagonal is a controlled diagnostic, not a reproduction of each original pipeline. Tree smoothing now uses the common expanded domain; N is ranked after common smoothing; F is also smoothed, unlike the original r4 fixed fusion. Therefore a diagonal change versus an original pipeline cannot be assigned solely to amount, architecture or averaging. Within a fixed amount column, predicted volume, signed volume error and absolute volume error are identical by construction. Equal error in those comparisons is not evidence of calibration. Within a fixed ranking row, amount changes the selected prefix and thus both overlap and topology.

All reported means weight patients equally. Intervals use 2,000 percentile patient bootstrap resamples with numpy default_rng(0); contrast intervals resample paired patient differences, including four-term interactions. Undefined endpoints are filtered separately. Dice/lesion F1 are one if both masks are empty; recall and matched recall are undefined for empty truth, precision and largest-component fraction for empty prediction. Fewer than three valid observations suppress estimates and intervals. These are conditional descriptive intervals, not multiplicity-adjusted confirmation or a noninferiority test. Shared saved fits, overlapping training sets, one split/realization, historical 69/30 exposure and repeated development-outcome use are not represented by this bootstrap. Neither folds, voxels nor components are independent extra patients. [S][S]; [CODE][CODE], summary, linear_rows; [L][L]

**The nine cells.** Entries are mean Dice [95% interval], all n=99. Rows hold ranking fixed; columns hold amount fixed. [F][F], groups.all.<ranking>__<amount>.metrics.dice

| Ranking | Tree amount | N amount | Fusion amount |
| --- | --- | --- | --- |
| tree | 0.2063 [0.1680, 0.2449] | 0.1702 [0.1293, 0.2111] | 0.2046 [0.1645, 0.2447] |
| nn | 0.2332 [0.1898, 0.2751] | 0.2045 [0.1583, 0.2506] | 0.2369 [0.1920, 0.2813] |
| fusion | 0.2467 [0.2035, 0.2894] | 0.2101 [0.1648, 0.2564] | 0.2491 [0.2034, 0.2942] |

Fusion ranking has higher mean Dice than either parent at every fixed amount. Its gain over T is about 0.04 absolute Dice; its gain over N is smaller. This supports complementary placement in these processed saved scores, not independent biological information or architectural superiority. The two prespecified primary summaries are N−T and F−T amount at F ranking: −0.0366 [−0.0555, −0.0174] and +0.0023 [−0.0061, +0.0108]. Thus N amount reduces overlap here; F amount provides no clear mean Dice improvement over T amount. The latter interval does not establish equivalence or preserved performance under a chosen tolerance. Corresponding mean Dice values are 0.2101, 0.2491 and 0.2467; their medians are 0.0624, 0.1598 and 0.1824, respectively, illustrating that the mean pattern does not describe every patient. [F][F], [C][C]

All 22 prespecified Dice contrasts follow, including the two primaries rather than selecting a favorable cell. “Amount X−Y at R” holds ranking R fixed; “Rank X−Y at A” holds amount A fixed. Interaction(r,a) is [M(r,a)−M(T,a)]−[M(r,T)−M(T,T)]. [C][C], terms and groups.all

| Contrast | Paired mean Dice change [95% interval] |
| --- | --- |
| Amount nn−tree at tree | -0.0361 [-0.0531, -0.0190] |
| Amount fusion−tree at tree | -0.0017 [-0.0087, 0.0058] |
| Amount fusion−nn at tree | 0.0344 [0.0219, 0.0477] |
| Amount nn−tree at nn | -0.0287 [-0.0448, -0.0130] |
| Amount fusion−tree at nn | 0.0037 [-0.0033, 0.0112] |
| Amount fusion−nn at nn | 0.0323 [0.0201, 0.0453] |
| Amount nn−tree at fusion | -0.0366 [-0.0555, -0.0174] |
| Amount fusion−tree at fusion | 0.0023 [-0.0061, 0.0108] |
| Amount fusion−nn at fusion | 0.0390 [0.0249, 0.0538] |
| Rank nn−tree at tree | 0.0269 [0.0078, 0.0468] |
| Rank fusion−tree at tree | 0.0404 [0.0280, 0.0542] |
| Rank fusion−nn at tree | 0.0135 [0.0020, 0.0256] |
| Rank nn−tree at nn | 0.0343 [0.0180, 0.0505] |
| Rank fusion−tree at nn | 0.0399 [0.0249, 0.0548] |
| Rank fusion−nn at nn | 0.0056 [0.0010, 0.0108] |
| Rank nn−tree at fusion | 0.0323 [0.0111, 0.0539] |
| Rank fusion−tree at fusion | 0.0445 [0.0298, 0.0604] |
| Rank fusion−nn at fusion | 0.0122 [0.0019, 0.0237] |
| Interaction(nn, nn) | 0.0074 [-0.0049, 0.0198] |
| Interaction(nn, fusion) | 0.0054 [-0.0008, 0.0115] |
| Interaction(fusion, nn) | -0.0006 [-0.0085, 0.0073] |
| Interaction(fusion, fusion) | 0.0040 [-0.0007, 0.0091] |

The N amount penalty recurs at all rankings (−0.0287 to −0.0366). F−T amount differences range from −0.0017 to +0.0037 with intervals spanning zero. F ranking gains over T remain positive at all amounts; no interaction interval excludes zero. This describes stability across these three saved amount rules, not universal separability or proof of no ranking–amount interaction.

**Amount accuracy and calibration limits.** All-99 source-amount summaries are independent of allocation feasibility and ranking. Signed error is predicted minus true ml; MAE is the mean patient absolute error. [A][A], groups.all.source_amounts

| Amount source | Predicted ml, mean [CI] | Signed error ml, mean [CI] | Absolute error ml, mean [CI] | Median absolute error ml |
| --- | --- | --- | --- | --- |
| tree | 30.39 [25.93, 35.15] | -3.54 [-11.94, 4.39] | 25.68 [19.59, 32.49] | 16.35 |
| nn | 17.27 [11.20, 23.89] | -16.66 [-24.26, -9.79] | 21.59 [15.21, 28.77] | 8.99 |
| fusion | 24.07 [19.09, 29.78] | -9.85 [-17.62, -2.70] | 21.37 [15.26, 28.22] | 9.76 |

Paired MAE changes are N−T −4.08 [−7.42, −0.80] ml, F−T −4.31 [−6.15, −2.48] ml, and F−N −0.23 [−2.16, +1.68] ml. Median signed errors are +8.23, −5.29 and +1.49 ml for T, N and F, while their mean signed errors are −3.54, −16.66 and −9.85 ml. Mean bias therefore conceals marked asymmetry and size dependence. F reduces absolute error relative to T despite a more negative mean bias. N improves MAE while worsening Dice: better amount estimation is not automatically better placement. For a predicted set of size k and truth of size t, Dice=2TP(k)/(k+t); changing k affects both numerator and denominator. Volume error only sees |k−t|. [A][A], groups.all.paired; [F][F]

This is an amount-error assessment, not a new probability-calibration experiment. These six outputs do not contain reliability curves, calibration slope/intercept, Brier scores, class-conditional Brier contributions, outer-training prevalence comparisons or predictive interval coverage for volume. The fusion count derives from a raw score sum, but its error does not by itself establish probability calibration. Existing earlier calibration conclusions are preserved; no recalibrator or threshold is fitted or promoted from this table.

**Patient-size strata.** Truth-total-volume groups contain one empty case, 28 positive cases below 5 ml, 50 cases from 5 to below 50 ml, and 20 cases at least 50 ml. All nine cells are retained in each group. The empty group's estimates and intervals are suppressed (n_valid=1 for Dice), not zero and not omitted from all-cohort scoring. Positive-group Dice follows. [F][F], groups; [I][I], stratum_counts

| Ranking / amount | 0 < truth < 5 ml (28) | 5 ≤ truth < 50 ml (50) | Truth ≥ 50 ml (20) |
| --- | --- | --- | --- |
| tree / tree | 0.0277 [0.0134, 0.0451] | 0.2193 [0.1732, 0.2696] | 0.4341 [0.3595, 0.5050] |
| tree / nn | 0.0204 [0.0062, 0.0412] | 0.1637 [0.1120, 0.2192] | 0.4046 [0.3026, 0.4975] |
| tree / fusion | 0.0320 [0.0148, 0.0541] | 0.2153 [0.1657, 0.2692] | 0.4297 [0.3474, 0.5066] |
| nn / tree | 0.0504 [0.0231, 0.0862] | 0.2523 [0.1948, 0.3123] | 0.4531 [0.3676, 0.5287] |
| nn / nn | 0.0378 [0.0109, 0.0702] | 0.2099 [0.1486, 0.2749] | 0.4349 [0.3262, 0.5323] |
| nn / fusion | 0.0563 [0.0224, 0.1007] | 0.2554 [0.1943, 0.3186] | 0.4551 [0.3626, 0.5393] |
| fusion / tree | 0.0495 [0.0237, 0.0831] | 0.2706 [0.2145, 0.3293] | 0.4757 [0.3945, 0.5502] |
| fusion / nn | 0.0419 [0.0140, 0.0768] | 0.2165 [0.1553, 0.2810] | 0.4400 [0.3310, 0.5396] |
| fusion / fusion | 0.0611 [0.0266, 0.1063] | 0.2718 [0.2116, 0.3358] | 0.4678 [0.3770, 0.5497] |

The small-patient group remains difficult under every cell: means span 0.0204–0.0611. At fusion ranking F−T amount is +0.0116 [0.0020, 0.0240] there, versus +0.0013 [−0.0102, 0.0133] in the middle group and −0.0079 [−0.0338, 0.0164] in the largest. The corresponding N−T amounts are −0.0076 [−0.0206, 0.0059], −0.0540 [−0.0808, −0.0267] and −0.0357 [−0.0929, 0.0166]. The clearest N amount Dice penalty is in the middle group; this is not a newly selected primary endpoint. These outcome-defined strata are diagnostic, not an admission-time routing variable. [C][C], groups.<stratum>.amount_*_rank_fusion

Stratified amount errors show why a single bias correction is not an established solution. Entries are mean signed error / mean absolute error in ml; full saved mean intervals for MAE are included. The singleton empty group remains suppressed for all three sources. [A][A], groups.<stratum>.source_amounts

| Truth stratum | Source | Mean signed error ml | MAE ml [95% interval] |
| --- | --- | --- | --- |
| positive_under5 | tree | 19.61 | 19.61 [15.52, 24.04] |
| positive_under5 | nn | 0.35 | 2.71 [1.78, 3.81] |
| positive_under5 | fusion | 10.17 | 10.17 [7.89, 12.59] |
| 5_to_under50 | tree | 6.55 | 13.27 [10.62, 16.38] |
| 5_to_under50 | nn | -9.18 | 13.85 [10.97, 17.02] |
| 5_to_under50 | fusion | -1.12 | 10.57 [7.98, 13.52] |
| 50_or_more | tree | -62.10 | 65.70 [44.47, 89.67] |
| 50_or_more | nn | -60.01 | 68.48 [47.65, 93.46] |
| 50_or_more | fusion | -60.59 | 64.70 [43.49, 89.15] |

For small patients, T and F mean overprediction is +19.61 and +10.17 ml, whereas N is +0.35 ml; paired MAE improvements versus T are −16.89 [−21.71, −12.51] ml for N and −9.43 [−11.80, −7.27] for F. Yet N amount does not restore spatial overlap. In the middle group T overpredicts by +6.55 ml, N underpredicts by −9.18 ml, and F bias is −1.12 ml; F−T MAE is −2.70 [−4.97, −0.32] ml. In the largest group all sources underpredict by about 60–62 ml, with MAE about 65–68 ml; F−T MAE −1.00 [−6.69, 4.20] and N−T +2.78 [−6.69, 11.49] do not establish improvement. These findings do not identify a biological subtype or support truth-size specialists at inference. [A][A]

**Components, fragmentation and detection.** Components use 26-connectivity and greedy one-to-one matching in descending IoU, requiring IoU ≥0.2, with deterministic truth/prediction label tie order. An unmatched predicted component is counted as false positive even if it overlaps truth but fails that matching rule. Merges count a predicted component overlapping multiple truth components; splits count a truth component overlapping multiple predicted components, independently of matching. Largest-component fraction is the share of predicted voxels in the largest predicted component. These topology measures have no regional or anatomical labels. Official-package equivalence is inherited from the notebook rather than freshly verified against the absent package. [S][S]; [CODE][CODE], component_metrics

Across the cohort the mean truth-component count is 9.8485 [8.1414, 11.6970], including means 9.1818 below 5 ml, 0.4747 at 5–<50 ml and 0.1919 at ≥50 ml. These are patient means of component counts, not patient counts. All nine cells' matching summaries follow. F1 and false-positive counts use n=99; matched recall uses n=98 because empty truth is undefined. [F][F], groups.all

| Ranking / amount | Lesion F1 [CI] | Matched-lesion recall [CI] | Unmatched predictions [CI] | Unmatched truth, mean |
| --- | --- | --- | --- | --- |
| tree / tree | 0.1087 [0.0713, 0.1536] | 0.0906 [0.0541, 0.1340] | 2.7071 [2.1313, 3.3333] | 9.5556 |
| tree / nn | 0.1058 [0.0644, 0.1503] | 0.0922 [0.0528, 0.1385] | 1.7778 [1.4141, 2.2323] | 9.5859 |
| tree / fusion | 0.1228 [0.0812, 0.1670] | 0.1089 [0.0681, 0.1551] | 2.6364 [2.1311, 3.2121] | 9.5253 |
| nn / tree | 0.1294 [0.0899, 0.1706] | 0.1233 [0.0798, 0.1714] | 3.5960 [3.0505, 4.2020] | 9.4545 |
| nn / nn | 0.1360 [0.0923, 0.1815] | 0.1151 [0.0721, 0.1633] | 1.1616 [0.9798, 1.3535] | 9.4848 |
| nn / fusion | 0.1336 [0.0915, 0.1791] | 0.1180 [0.0747, 0.1659] | 2.7475 [2.3333, 3.2121] | 9.4848 |
| fusion / tree | 0.1347 [0.0923, 0.1772] | 0.1243 [0.0797, 0.1736] | 2.8485 [2.2929, 3.4750] | 9.4646 |
| fusion / nn | 0.1374 [0.0926, 0.1838] | 0.1142 [0.0714, 0.1624] | 1.2323 [1.0404, 1.4444] | 9.4949 |
| fusion / fusion | 0.1395 [0.0950, 0.1858] | 0.1240 [0.0791, 0.1731] | 2.3131 [1.8987, 2.7677] | 9.4747 |

Fragmentation summaries below are mean [95% interval], n=99. A larger largest-component fraction does not imply anatomical correctness; fewer components may also accompany reduced recall. [F][F], groups.all

| Ranking / amount | Predicted components | Largest-component fraction | Merges | Splits |
| --- | --- | --- | --- | --- |
| tree / tree | 3.000 [2.455, 3.596] | 0.870 [0.828, 0.908] | 0.364 [0.263, 0.485] | 0.111 [0.061, 0.182] |
| tree / nn | 2.040 [1.677, 2.475] | 0.891 [0.853, 0.924] | 0.131 [0.071, 0.202] | 0.101 [0.040, 0.162] |
| tree / fusion | 2.960 [2.485, 3.505] | 0.848 [0.809, 0.887] | 0.273 [0.182, 0.364] | 0.131 [0.071, 0.202] |
| nn / tree | 3.990 [3.475, 4.566] | 0.758 [0.715, 0.801] | 0.293 [0.202, 0.384] | 0.172 [0.101, 0.253] |
| nn / nn | 1.525 [1.364, 1.697] | 0.921 [0.889, 0.949] | 0.091 [0.040, 0.152] | 0.101 [0.040, 0.162] |
| nn / fusion | 3.111 [2.737, 3.515] | 0.792 [0.751, 0.833] | 0.242 [0.162, 0.333] | 0.141 [0.081, 0.212] |
| fusion / tree | 3.232 [2.707, 3.848] | 0.857 [0.815, 0.894] | 0.384 [0.283, 0.505] | 0.141 [0.081, 0.212] |
| fusion / nn | 1.586 [1.434, 1.758] | 0.912 [0.880, 0.940] | 0.121 [0.061, 0.182] | 0.061 [0.020, 0.111] |
| fusion / fusion | 2.687 [2.293, 3.101] | 0.855 [0.818, 0.890] | 0.253 [0.162, 0.343] | 0.131 [0.071, 0.192] |

At tree amount, F−T ranking raises matched recall by +0.0337 [0.0092, 0.0650] and reduces unmatched truth by 0.0909 [0.0404, 0.1515] components per patient. Its lesion-F1 difference is +0.0260 [−0.0028, 0.0553], and unmatched predictions change by +0.1414 [−0.2020, 0.4646]. This supports a placement improvement with some matching improvement, but does not establish a global detection advantage or absence of harm.

At tree amount, F versus N ranking has 0.7576 fewer predicted components [0.2222, 1.2730], 0.7475 fewer unmatched predictions [0.2318, 1.2626], and +0.0981 [0.0555, 0.1430] largest-component fraction, but +0.0909 [0.0101, 0.1717] merges. Splits change −0.0303 [−0.0909, 0.0303]. Thus “less fragmentation” is only a partial description of the measured pattern; it does not prove merging caused the Dice gain or that regions were recovered correctly. [C][C], rank_fusion_minus_*_amount_tree

At F ranking, replacing T amount with N reduces mean predicted volume by 13.12 ml, raises precision by +0.0838 [0.0523, 0.1167] (99 patients), and lowers voxel recall by −0.1251 [−0.1609, −0.0909] (98). It reduces predicted components by 1.6465 [1.1313, 2.2323], unmatched predictions by 1.6162 [1.0909, 2.2020], merges by 0.2626 [0.1717, 0.3636] and splits by 0.0808 [0.0202, 0.1515]. Largest-component fraction rises by 0.0554 [0.0164, 0.0957]. Despite that apparent tidiness, Dice falls and lesion-F1 change +0.0027 [−0.0176, 0.0200] is uncertain. F amount instead reduces volume by 6.31 ml, raises precision +0.0218 [0.0136, 0.0308] and lowers recall −0.0403 [−0.0527, −0.0277]; F1 changes +0.0048 [−0.0037, 0.0163]. Its largest-component fraction and splits have intervals spanning zero. No pruning or smoothing mechanism has been causally isolated. [C][C], amount_*_minus_tree_rank_fusion

Patient size and component size must remain separate. Across 93 patients containing a <5 ml truth component, patient-averaged small-component matched recall ranges only 0.0023–0.0072 over the nine cells. For F/F it is 0.0072 [0.0000, 0.0197], compared with 0.4545 [0.3182, 0.6136] for 5–<50 ml components (44 contributing patients) and 0.7368 [0.5263, 0.8947] for ≥50 ml components (19). No component-weighted detection rate is substituted for these patient averages. At tree amount F−T improves middle-component recall by +0.1364 [0.0455, 0.2500], whereas its small-component gain is +0.0045 [0.0000, 0.0116]. [F][F], component_recall_bin1/2/3; [C][C]

Within the 28 small-total-volume patients, tree ranking has zero matched recall and lesion F1 at every amount. The zero-width bootstrap intervals [0,0] reflect those realized saved values, not certainty about a population. F/F has matched recall 0.0060 [0, 0.0179], F1 0.0051 [0, 0.0153], 9.8214 unmatched truth components and 3.4286 unmatched predicted components per patient. In middle and large patients F/F matched recall is 0.1269 [0.0679, 0.1943] and 0.2820 [0.1463, 0.4483]; unmatched truth means remain 10.38 and 7.20. Among the 17 large-total-volume patients containing small components, no cell matches a small component under this rule. Their middle-component recall has only two valid patients and is suppressed. Empty and absent component bins remain null, not zero-valued performance. The deficit therefore extends beyond small-total-volume patients, but neither prospective visibility nor an anatomical cause was measured. [F][F], groups.positive_under5/5_to_under50/50_or_more/empty

**Feasibility and support.** All 891 expected cells are feasible (99 per cell), with zero infeasible source-amount substitutions in every stratum. The 2,673 amount-identity checks have maximum error zero. Fusion's original cap is triggered in zero patients, cap-loss voxels are zero; its uncapped request mean is 3,009.22 voxels [2,386.09, 3,722.34]. No silent clamping explains the results. Had a substituted count exceeded capacity, its three cells would have remained infeasible, paired estimates would have used jointly feasible patients, and all-99 amount errors would still have been reported. That potential selection limitation exists in the design but did not reduce denominators in this return. [I][I], [A][A]

Full-truth scoring retains mean outside-domain truth of 0.7272 [0.4164, 1.1463] ml (median 0.0720); corresponding means are 0.0980, 0.4914 and 2.2340 ml in small, middle and large positive strata. The singleton empty estimate is suppressed. This measures excluded truth volume, not anatomical scan coverage, a Dice ceiling or the full explanation of misses. No centre-balanced estimate, regional accuracy, territory analysis, clinical outcome, treatment interaction, prospective utility or independent registration-quality measurement is present in these six outputs. Centre mapping and matched normalization evidence are unavailable in this input scope. Upstream acquisition timing, feature/support generators, annotation assistance and native reader plans remain incompletely verified. Agreement with saved segmentation and cache geometry cannot resolve those upstream gaps. [A][A], [S][S], [L][L]

**Relation to prior evidence and retained omissions.** In the inspected external r4 aggregate, original tree mean Dice was 0.208 and fixed unsmoothed fusion 0.228; original fusion lesion F1 was 0.051 versus tree 0.109. Those results retain their original definitions and historical detection penalty. Current F/F Dice 0.2491 and F1 0.1395 belong to a different common-smoothed diagnostic; their difference from r4 is not a paired treatment effect and does not overturn the earlier judgment. The r4 notebook and its aggregate archive overlap the same outside execution, not independent repetitions. The historical stocktake's retain-tree/no-calibration-promotion/inconclusive-cached-CNN conclusions are likewise not rewritten. [R4][R4], cells4/6 source and saved outputs; [EXT][EXT], sprint13a_methods.csv; [DIR][DIR], Ranked comparison; [STOCK][STOCK], Sprints5/5b

The [navigation index][NAV] registers no per-patient material in either selected scientific view. **Per-patient evidence used here: none; registered per-patient reasons: none.** No identifiers, rows, masks, scores or labels were opened. Aggregate denominators and receipts are the only patient-related evidence used. The [r4 omissions][OM1], SHA256 `0e4b6b24ce24041329d47fa9ea7ac420223d185f51a3e50d50142739f977d911`, preserve the uninspected notebook metadata/type units, output metadata and two JavaScript rendered units. The original notebook is `6432e7d31fa50274320fdc31759c698908a649dc48ab6e9928cbbbe18ee265e6`; the selected view is `e69a664e081ad1770454c6ce453ff4ddad3b16d2876f889ca89f8f876bb1d72b`. The [archive omissions][OM2], SHA256 `5a52ab34051166bc70aa9173f114034eca6b93045615dd92e5c2876878dee56c`, retain omitted `sprint13a_precision_recall.png` and `sprint13a_dice_tree_vs_nnunet.png`; archive identity is `bdf0a546052899d0a82aee70676abe5ff22c949f88f73287249891bab517b9a3`. Those images and all omitted units remain uninspected. Citations inside historical documents do not imply their absent underlying originals were inspected here.

**Proposed next ideas, separate from observations.** The following are prospective hypotheses, not tested improvements. They use the existing mathematical decomposition and measured small-component deficit; no literature search or novelty claim is made.

1. **A small, fully nested amount model with fixed ranking.** Uncertainty: can admission-derived predictions reduce size-dependent amount error without sacrificing overlap? Mechanism: decouple ordering from a low-dimensional estimate of selected volume; the three saved rules already demonstrate that MAE and Dice can move in different directions. Existing legwork is the common-domain ranking comparison and source-amount error profile. The smallest discriminating comparison would retain one prespecified fusion ranking and compare its frozen amount rule against a simple nonnegative amount model using prediction-derived scalar summaries only. Base fits and amount-model fitting/tuning must all remain inside each outer training partition; ordinary meta-fitting to the present cross-validated rows is insufficient because their base training sets overlap the scored fold. Measure paired all-patient Dice, MAE, signed error, precision/recall and component endpoints, with all fixed size strata and training-repeat uncertainty. A lower MAE alone is not success. The dangerous confound is using exposed outcomes or leaked base fits to choose the mapping, exacerbated by the small cohort. A negative result would limit this low-dimensional correction rather than rule out better admission predictors. It would answer the charter's investment question more directly than training separate truth-size specialists.

2. **One prespecified smoothing sensitivity at fixed amount for the small-component deficit.** Uncertainty: are some component misses associated with the processing scale, or do the saved raw scores already fail to rank them? Mechanism: smoothing averages local score peaks; a smaller component can lose rank even when total selected volume is held constant. This is a mathematical possibility, not a measured biological cause. Existing legwork is the shared-grid/common-domain implementation and near-zero small-component recall, including small components in large-total-volume patients. The smallest discriminating saved-output analysis would compare the existing width with one fixed zero-smoothing comparator at the same prespecified amount and domain, without a width sweep. Measure paired small-component matched recall, unmatched predictions, Dice, merges/splits and largest-component fraction, retaining patient-total-size and component-size bins separately. The dangerous confounds are registration/resampling errors, tiny annotation components, score ties and the IoU matching threshold; no change of matching rule should be folded into this contrast. A negative result would weaken this specific smoothing explanation; a positive result would still require a benefit–false-positive tradeoff assessment. It would not identify regions, prove admission visibility or justify pruning.

3. **A source-only provenance trace before interpreting these as admission-ready predictions.** Uncertainty: which feature/support inputs were available by the admission cutoff, and what annotation work produced them? Mechanism: a dependency and timestamp trace can separate intended input names from actual acquisition/processing availability without changing model outputs. The existing cache/mask reconciliation and desk-audit gaps provide the starting point. The smallest decisive analysis would inspect original generator source, acquisition metadata and feature definitions, recording each dependency as verified admission-available, later information, annotation-assisted or unresolved. Its discriminating measurement is a complete dependency/timing table with evidence for each classification, not a performance score. The dangerous confound is treating filenames, source comments or successful hash checks as timing proof. An unresolved or adverse result would still clarify which prospective claim or future comparison is meaningful; it would not invalidate the measured saved-output arithmetic by itself.

The bounded interpretation ends with return of this evidence to the operator. Its scientific answer is useful but narrow: fusion placement improves over tree under the fixed controls; saved amount substitution can improve absolute volume error without improving Dice; small-component detection remains poor. This endpoint does not end the broader follow-up infarct-prediction research question.

**Full stratified Dice contrasts.** The table retains all 22 prespecified contrasts in every positive patient-size stratum. The empty stratum has n_valid=1 for every Dice contrast and all its estimates/intervals are suppressed. Other endpoint-specific valid counts, medians and intervals remain in the linked complete original F/C/A files; no unreported endpoint is treated as favorable or null. [C][C], groups

| Contrast | Positive <5 ml (28) | 5–<50 ml (50) | ≥50 ml (20) |
| --- | --- | --- | --- |
| Amount nn−tree at tree | -0.0072 [-0.0208, 0.0054] | -0.0556 [-0.0801, -0.0317] | -0.0295 [-0.0854, 0.0221] |
| Amount fusion−tree at tree | 0.0043 [-0.0007, 0.0102] | -0.0040 [-0.0137, 0.0056] | -0.0044 [-0.0295, 0.0192] |
| Amount fusion−nn at tree | 0.0115 [-0.0005, 0.0246] | 0.0516 [0.0324, 0.0731] | 0.0250 [-0.0029, 0.0563] |
| Amount nn−tree at nn | -0.0126 [-0.0253, 0.0000] | -0.0424 [-0.0665, -0.0202] | -0.0182 [-0.0650, 0.0241] |
| Amount fusion−tree at nn | 0.0060 [-0.0040, 0.0168] | 0.0031 [-0.0083, 0.0143] | 0.0020 [-0.0166, 0.0213] |
| Amount fusion−nn at nn | 0.0185 [0.0066, 0.0360] | 0.0455 [0.0271, 0.0662] | 0.0203 [-0.0033, 0.0480] |
| Amount nn−tree at fusion | -0.0076 [-0.0206, 0.0059] | -0.0540 [-0.0808, -0.0267] | -0.0357 [-0.0929, 0.0166] |
| Amount fusion−tree at fusion | 0.0116 [0.0020, 0.0240] | 0.0013 [-0.0102, 0.0133] | -0.0079 [-0.0338, 0.0164] |
| Amount fusion−nn at fusion | 0.0191 [0.0042, 0.0385] | 0.0553 [0.0338, 0.0776] | 0.0278 [-0.0010, 0.0590] |
| Rank nn−tree at tree | 0.0227 [0.0001, 0.0500] | 0.0329 [0.0002, 0.0649] | 0.0190 [-0.0173, 0.0564] |
| Rank fusion−tree at tree | 0.0218 [0.0044, 0.0461] | 0.0512 [0.0314, 0.0720] | 0.0416 [0.0185, 0.0654] |
| Rank fusion−nn at tree | -0.0009 [-0.0107, 0.0098] | 0.0183 [-0.0010, 0.0399] | 0.0226 [0.0048, 0.0449] |
| Rank nn−tree at nn | 0.0174 [-0.0059, 0.0474] | 0.0461 [0.0209, 0.0721] | 0.0302 [0.0044, 0.0563] |
| Rank fusion−tree at nn | 0.0215 [-0.0008, 0.0513] | 0.0528 [0.0296, 0.0773] | 0.0353 [0.0134, 0.0562] |
| Rank fusion−nn at nn | 0.0041 [-0.0022, 0.0113] | 0.0066 [-0.0007, 0.0156] | 0.0051 [-0.0018, 0.0121] |
| Rank nn−tree at fusion | 0.0244 [-0.0051, 0.0613] | 0.0401 [0.0047, 0.0756] | 0.0254 [-0.0043, 0.0566] |
| Rank fusion−tree at fusion | 0.0291 [0.0055, 0.0675] | 0.0565 [0.0341, 0.0801] | 0.0381 [0.0157, 0.0607] |
| Rank fusion−nn at fusion | 0.0047 [-0.0079, 0.0202] | 0.0165 [-0.0031, 0.0369] | 0.0126 [0.0012, 0.0256] |
| Interaction(nn, nn) | -0.0053 [-0.0169, 0.0064] | 0.0132 [-0.0074, 0.0342] | 0.0112 [-0.0111, 0.0369] |
| Interaction(nn, fusion) | 0.0017 [-0.0086, 0.0133] | 0.0071 [-0.0030, 0.0171] | 0.0064 [-0.0035, 0.0188] |
| Interaction(fusion, nn) | -0.0003 [-0.0109, 0.0097] | 0.0016 [-0.0124, 0.0153] | -0.0063 [-0.0181, 0.0048] |
| Interaction(fusion, fusion) | 0.0073 [-0.0007, 0.0203] | 0.0053 [-0.0019, 0.0121] | -0.0035 [-0.0088, 0.0008] |

[F]: /workspace/evidence/149725bb7277864c25b360185ca0d8306a82b72149ac51a1435720871df39582-7fd4b42829c2309e3638626acad340eacc062297b8707956b546645fc8bf9c4e-result_tables.txt
[C]: /workspace/evidence/63b4e91fb6fec51493e832745fa50706b16ed2aa6076eeadb41fee9be2e024e6-931b427722e2a53585a4a861afd349c798cf43e4d61cac6ccd36466b9c8b7a87-result_tables.txt
[A]: /workspace/evidence/84993970fe8a99f53530e4804c3557e0ea2cbdb9f525ae69bd28d1f2b63dedc6-078e03c6986e02fe746ce4d383b02b29fdc01973275c8222b76f2911506dea4e-result_tables.txt
[I]: /workspace/evidence/da29934de8b554337a6c41d7a883ac87d8ba1740093d085b75219be8f273d366-17c97a2a2e9acb6e6c1afbd6af43e2e218bb1af4ba979e95d99b4255c154b5af-result_tables.txt
[L]: /workspace/evidence/1c988644eb94536c4838a164c01a33a0829ecf2543a91a75a3bd0cf7d7f0be89-9410fe98b37c077f79161519681a4e8dda009e545bd2fcb191d2bca5cd53c8aa-result_tables.txt
[V]: /workspace/evidence/ca49da2e80b2de14452c2dc8c61bd1c0d20f3eb199bc3d6e73eaa90cb10dd930-dbb2a11e3894a79d1a4afe564f987c4aa6cba25752c53ab59de56859c1ec6970-validation_result.txt
[S]: /workspace/evidence/462d91cb9c351832cccc0b9c5f572a0b09e9e57a242b68ec163c52347ba507db-541f98211ea49d58b085bef3e38eebd8e976e29f4e5aae24d63b37f6eda50197-run_spec.txt
[P]: /workspace/evidence/830d9a6036cf20372470674081ae1d48a56941f219afe200b4fce98c879687c7-f409492f8d2e2c69a6cc097f2c054fdaf322523bbdca4381e0d766ad208e5164-package_manifest.txt
[CODE]: /workspace/evidence/cea229e28e9905bf046a1c2054c3b74b17c8b2ed0f132e0018e77baa9e41e5d4-1fa543aa4bb709993fb5561196ca09e5f73f0912426590d9b31e33e4d0eb970f-analysis_source.txt
[TEST]: /workspace/evidence/008be90a773f4dcbb0ae9a698c10415d31416af89a1d4a97688c5b95c496bf93-b5f9e7733e18d3e7a25a2457edacf12c1c2b351f6b24dae939e8c00c233b0396-synthetic_tests.txt
[PROV]: /workspace/evidence/f4a43a821ec87beb9f6b0fb5b09c53ebc84adf2a1b13115172d37b74fa799ad1-01995eb16e5b6fa299bbbf8bd0a821cc511453d0dcbb99706b43df34bf385409-analysis_provenance.txt
[FIND1]: /workspace/evidence/2fe1ce22f30264d92f1cc03b81f0940c78684000c27ce9353fdae1f586eb12bf-finding.json
[FIND2]: /workspace/evidence/815367d0ad9b7109848ba3bc866b0cad30e775b221f0bedde545cb7e8a7f6380-finding.json
[NAV]: /workspace/evidence/784ada98298a865edf1a27c12a1cb164a7fffe029da53a3fd13c10d4f8bb58f6-private-index.json
[OM1]: /workspace/evidence/0e4b6b24ce24041329d47fa9ea7ac420223d185f51a3e50d50142739f977d911-sprint13a-r4-completed-omissions.json
[OM2]: /workspace/evidence/5a52ab34051166bc70aa9173f114034eca6b93045615dd92e5c2876878dee56c-Sprint13A-completed-aggregates-omissions.json
[R4]: /workspace/evidence/e69a664e081ad1770454c6ce453ff4ddad3b16d2876f889ca89f8f876bb1d72b-sprint13a-r4-completed-view.txt
[EXT]: /workspace/evidence/e5cb1b3e0bb35fdd8aa5cb613390951f5c4636c8fa59edf692737a1084344195-Sprint13A-completed-aggregates-view.txt
[DIR]: /workspace/evidence/bf6e4ffab3f54c77da4e9aa97f764074a4496dfdbc2253445d17d2e0d5d86138-94098d89319371a16c20b1f6a2b50b1cea563de572ffd2691a2240d726faa645-prior_results.txt
[STOCK]: /workspace/evidence/26abd688a46f9677af9a572fcdbe0958d711d8fe1b8ea9444ae8cb87a8f563c0-05319d27f6c9c9ebf0b032d7c22a994d58cfac7b275bd490d94a84169b95a5ba-prior_results.txt
[PRE]: /workspace/evidence/8fa55d40944de8d8455f98d70ea2db5a08e7da8dbb7f0a2a0156f4490ba821a4-ebc1c08918f775f61563448f69a8052c4c05a6b3db122eb13e2c156030309bca-prior_results.txt


This accepted saved-output analysis preserves the original item6 acceptance and all calls. It authorizes no successor execution.
