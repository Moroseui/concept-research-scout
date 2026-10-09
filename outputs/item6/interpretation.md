# Summary

Does combining the tree and nnU-Net improve where infarct tissue is predicted when predicted volume is held constant? Yes, within these 99 development patients: mean Dice rose from 0.2063 to 0.2467, a paired gain of 0.0404 (95% patient-bootstrap interval 0.0280–0.0542). This supports a placement benefit for the frozen rule, but not clinical effectiveness. The original own-volume fusion still lost lesion-detection F1 and produced many unmatched components. Small-infarct performance remained poor. The fixed size router selected the tree for every patient, so it added nothing. Calibration showed substantial score–event mismatch. Centre effects and admission availability remain unresolved; all patients also fell into one coverage stratum. Results reuse exposed development patients and saved fitted models, so intervals omit training, selection and transfer uncertainty. Stop this diagnostic branch without promoting the router or specialist training from these results.

# Details

The evidence supports a completed aggregate diagnostic return for `diagnostics-b203ee1ce27e909d9d78d44a`. All five diagnostics were represented in one CPU-only, no-training execution, but centre/normalization comparisons and upstream admission verification remain scientifically incomplete. No computation on patient data, implementation change, experimental rerun or additional model call was performed in this interpretation workspace. Local checks compared artifact bytes and inspected already returned aggregates.

**Execution evidence and its limits.** The execution manifest and receipt were inspected in their selected representations in `prompt.md` (original identities listed below); their original paths are not separately mounted here. The receipt names provider `sb-01M4CTVGT1CC1CSPY149KG94BK`, binding SHA256 `6c6e617ac31cfc6cefb7426c7a4b4a45159c19dd4dc7acd56e90a12aecb3a173`, passing native preflight and full before/after rehashes of 728 input files and 30 package files. The read-only control passed; deliberately writable data/package controls were rejected. These controls are infrastructure evidence, not patient performance experiments.

The separately inspected package manifest records package SHA256 `59815ec499d344312fe14eeca0f89bd0299501b8b455a7b13b07a4cc1d8d930c` and reviewed-execution SHA256 `552e77dd1f33459a6438be18c7178d97495455cf0ada0fe4fe48cad89fa4ebc9`. It is a two-identity manifest, not a locally supplied full package inventory. Validation binds source `8e0423395d650bf757780c8c0877d7801815514a`, specification `4956d0d133f11de517486865858857f26f1f49e3549964ca0ac971ce90dc263f`, analysis source `ef1c1eb749bb477d83baffbdde771824234b6dfd75fb30fd80665860d27f61cc`, execution plan `613bb59adc7836c8a4120e0ff9e6e2df5befe6d643bb263e0a86cc84dca228a5`, and patient-execution environment `a995dca9bf3e4fdc01af0d8f1094682bf71d534d0a029e369ea2eebddf7ca258`. Program identity is `f647c012c3ed1d36b451f5805f8da569e010d04f35864e5aad723415e446e5ff` in both execution manifest and analysis provenance. Input contract is `8c9a1eb91016f435baaf4fe03bb82109ece7c70d09d42488fea327c067df186e`; capture is `c742b81d9f561dec9cb330c8f4b59f6c9df36b5136819f3bbf1a171c8891b119`; cohort is `45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86`.

All eight declared files are present. Their SHA256 values agree with the execution receipt; seven output sizes/hashes also agree with `validation.json`. All eight validation checks report PASS. The measured integrity output accounts for 99 patients in folds 20/20/20/20/19, 297 mask checks, 99 exactly recomputed probability caches and 1,188 table comparisons with maximum absolute discrepancy 0. Native probability-threshold versus saved segmentation Dice is 1.0 for all 99. This supports the saved-input arithmetic, including the frozen transpose/resampling convention; absent reader plans and upstream generators still limit independent provenance verification. No original official metric package was inspected: equivalence is the external notebook's attribution. Actual patient-run duration, billed cost, token use and intervention time are unavailable in these selected records. The 16.09-second synthetic duration is not the patient-run duration.

**1. Placement at fixed amount.** Each method selected the saved tree voxel count, with identical frozen Gaussian smoothing and deterministic ties. Candidate support is tissue support union nnU-Net probability >0.0001; common-support sensitivity restricts ranking to tissue support while retaining full truth. All 594 amount checks had zero discrepancy and no common-domain infeasibility. Therefore equal volume error is imposed, not evidence of accurate amount estimation. Sources: `placement.json` → `groups`, `paired`, amount checks; inspected analysis source → `analyse_case`, `smooth`, `topk`.

| Paired comparison | Mean Dice difference [95% interval] | Lesion-F1 difference [95% interval] |
|---|---:|---:|
| candidate_fusion_minus_tree | 0.0404 [0.0280, 0.0542] | 0.0260 [-0.0028, 0.0553] |
| candidate_nn_minus_tree | 0.0269 [0.0078, 0.0468] | 0.0208 [-0.0104, 0.0529] |
| common_fusion_minus_tree | 0.0389 [0.0271, 0.0522] | 0.0257 [-0.0002, 0.0525] |
| common_nn_minus_tree | 0.0289 [0.0095, 0.0484] | 0.0256 [-0.0045, 0.0574] |

All paired Dice/F1 denominators are 99. Candidate fusion matched-lesion recall increased by 0.0337 [0.0092, 0.0650], valid n=98. The primary Dice interval supports better placement conditional on these saved fits; lesion-F1 uncertainty includes a small decrement and does not establish noninferiority. Similar common-support findings weaken the explanation that the gain comes solely from expanded candidate support. They do not isolate architecture, biological information or an optimal fusion weight. This smoothed, fixed-amount fusion differs from the unsmoothed own-volume fusion below; the gain cannot simply be assigned to the original r4 rule.

All actual patient-volume strata are retained below. Values are mean Dice; the empty-truth singleton retains its count with numeric summaries suppressed. Each row uses the full truth mask.

| Actual truth volume | n | Candidate tree | Candidate nn | Candidate fusion | Common tree | Common nn | Common fusion |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 99 | 0.2063 | 0.2332 | 0.2467 | 0.2082 | 0.2371 | 0.2471 |
| empty | 1 | — | — | — | — | — | — |
| positive_under5 | 28 | 0.0277 | 0.0504 | 0.0495 | 0.0277 | 0.0573 | 0.0505 |
| 5_to_under50 | 50 | 0.2193 | 0.2523 | 0.2706 | 0.2206 | 0.2551 | 0.2699 |
| 50_or_more | 20 | 0.4341 | 0.4531 | 0.4757 | 0.4404 | 0.4557 | 0.4780 |

**2. Small lesions, components and routing.** `components.json` retains seven methods, all four actual-size strata and the whole cohort; all six fusion/union/router comparisons against both parents are preserved under `paired_by_group`. Component matching uses 26-connectivity and descending-IoU greedy one-to-one matches at IoU ≥0.2. Merge/split counts instead describe any-overlap topology and are not successful matches. Values below are patient means. MAE is mean absolute volume error in ml, not the historical median-error endpoint. FP means unmatched predicted components under this matching rule, not necessarily zero-overlap components.

| Actual truth volume | n | Method | Dice | Lesion F1 | MAE ml | FP components |
|---|---:|---|---:|---:|---:|---:|
| all | 99 | tree | 0.2082 | 0.1086 | 25.677 | 2.737 |
| all | 99 | unet | 0.1938 | 0.0879 | 37.307 | 4.808 |
| all | 99 | nn | 0.1998 | 0.0809 | 21.595 | 4.404 |
| all | 99 | union | 0.2392 | 0.0932 | 25.395 | 5.788 |
| all | 99 | fusion_own | 0.2277 | 0.0506 | 21.367 | 44.273 |
| all | 99 | router | 0.2082 | 0.1086 | 25.677 | 2.737 |
| all | 99 | nn_after_resampling | 0.1989 | 0.0803 | 21.627 | 4.101 |
| empty | 1 | tree | — | — | — | — |
| empty | 1 | unet | — | — | — | — |
| empty | 1 | nn | — | — | — | — |
| empty | 1 | union | — | — | — | — |
| empty | 1 | fusion_own | — | — | — | — |
| empty | 1 | router | — | — | — | — |
| empty | 1 | nn_after_resampling | — | — | — | — |
| positive_under5 | 28 | tree | 0.0277 | 0.0000 | 19.607 | 3.929 |
| positive_under5 | 28 | unet | 0.0307 | 0.0000 | 35.636 | 5.357 |
| positive_under5 | 28 | nn | 0.0381 | 0.0094 | 2.715 | 4.786 |
| positive_under5 | 28 | union | 0.0338 | 0.0100 | 21.516 | 7.107 |
| positive_under5 | 28 | fusion_own | 0.0435 | 0.0015 | 10.175 | 59.107 |
| positive_under5 | 28 | router | 0.0277 | 0.0000 | 19.607 | 3.929 |
| positive_under5 | 28 | nn_after_resampling | 0.0369 | 0.0029 | 2.688 | 4.536 |
| 5_to_under50 | 50 | tree | 0.2206 | 0.0968 | 13.275 | 2.680 |
| 5_to_under50 | 50 | unet | 0.1767 | 0.0480 | 30.656 | 5.980 |
| 5_to_under50 | 50 | nn | 0.2003 | 0.0715 | 13.845 | 4.260 |
| 5_to_under50 | 50 | union | 0.2447 | 0.0861 | 16.033 | 5.660 |
| 5_to_under50 | 50 | fusion_own | 0.2417 | 0.0364 | 10.575 | 46.880 |
| 5_to_under50 | 50 | router | 0.2206 | 0.0968 | 13.275 | 2.680 |
| 5_to_under50 | 50 | nn_after_resampling | 0.1996 | 0.0720 | 13.860 | 3.960 |
| 50_or_more | 20 | tree | 0.4404 | 0.2955 | 65.699 | 0.950 |
| 50_or_more | 20 | unet | 0.4745 | 0.3151 | 57.739 | 1.100 |
| 50_or_more | 20 | nn | 0.4348 | 0.2088 | 68.476 | 4.300 |
| 50_or_more | 20 | union | 0.5248 | 0.2318 | 54.732 | 4.000 |
| 50_or_more | 20 | fusion_own | 0.4622 | 0.1572 | 64.697 | 14.300 |
| 50_or_more | 20 | router | 0.4404 | 0.2955 | 65.699 | 0.950 |
| 50_or_more | 20 | nn_after_resampling | 0.4339 | 0.2134 | 68.636 | 3.900 |

Own-volume fusion versus tree improves Dice by 0.0195 [0.0070, 0.0324] and reduces mean absolute error by 4.310 ml [2.480, 6.146], but reduces lesion F1 by 0.0580 [0.0310, 0.0887]. Against nnU-Net, fusion gains 0.0280 [0.0162, 0.0406] Dice while losing 0.0304 [0.0145, 0.0478] lesion F1; its MAE difference is −0.228 [−2.159, 1.682] ml. Fusion has 44.27 unmatched predicted components per patient versus tree 2.74 and nnU-Net 4.40. Its mean splits are 0.545 versus 0.131/0.212, and merges 0.343 versus 0.374/0.121. This is consistent with excess components contributing to the F1 penalty, but is not a causal decomposition of that penalty.

Union versus tree gains 0.0310 [0.0221, 0.0403] Dice, with F1 difference −0.0154 [−0.0391, 0.0064] and MAE difference −0.282 [−2.623, 1.967] ml. Against nnU-Net, union gains 0.0394 [0.0195, 0.0598] Dice but worsens MAE by 3.800 [0.214, 7.609] ml. In the 28 positive patients below 5 ml, union versus tree gains only 0.0061 [0.0013, 0.0124] Dice and worsens MAE by 1.908 [0.900, 3.204] ml. Its Dice difference against nnU-Net is −0.0043 [−0.0230, 0.0124]. Small-patient-bin overlap remains low for every method; no universal patient-level failure is inferred from group means.

The router's union branch was used 0 times: every tree prediction was at least 5 ml. Router–tree differences are exactly zero, including their bootstrap intervals, in all estimable strata. This is an inactive intervention on this cohort, not evidence of general equivalence or failed specialist training. Actual-size rows versus predicted-tree-size columns, ordered empty, positive <5, 5–<50, ≥50 ml, are respectively `[0,0,1,0]`, `[0,0,27,1]`, `[0,0,48,2]`, `[0,0,10,10]`. Thus none of the 28 truly small positive cases triggered the small-prediction branch. No threshold revision is inferred from this table.

Individual component sizes differ from total patient infarct sizes. Mean patient-level matched-component recall for component bins <5 / 5–<50 / ≥50 ml has valid denominators 93 / 44 / 19 patients. All methods are retained:

| Method | Component <5 ml | Component 5–<50 ml | Component ≥50 ml |
|---|---:|---:|---:|
| tree | 0.0027 | 0.3523 | 0.6842 |
| unet | 0.0027 | 0.1591 | 0.7895 |
| nn | 0.0036 | 0.3636 | 0.7368 |
| union | 0.0058 | 0.4205 | 0.7368 |
| fusion_own | 0.0108 | 0.4318 | 0.7368 |
| router | 0.0027 | 0.3523 | 0.6842 |
| nn_after_resampling | 0.0009 | 0.3636 | 0.7368 |

Resampling probabilities before thresholding instead of the saved native-threshold/nearest-resampled mask changes Dice by −0.000879 [−0.001541, −0.000216] and lesion F1 by −0.000643 [−0.005294, 0.002343], n=99. That specific geometry sensitivity is small at the cohort mean; it does not exclude other preprocessing explanations. All component count, matched count, recall, precision, signed-error, median and interval fields remain in the original output, including undefined values and the suppressed singleton.

**3. Calibration.** `calibration.json` → `curves` contains all ten frozen reliability bins and eight method/domain combinations. Brier scores below are patient means; brackets are saved 95% intervals. Full-grid zero extension and common tissue support answer different questions. Probability-sum error is signed prediction minus truth; common-support errors refer only to that domain.

| Score | Domain | Brier [95% interval] | Probability-sum error ml [95% interval] |
|---|---|---:|---:|
| tree | full_grid | 0.002746 [0.002126, 0.003414] | -3.538 [-11.936, 4.387] |
| tree | common_support | 0.022153 [0.017114, 0.027532] | -1.388 [-9.140, 5.919] |
| unet | full_grid | 0.003564 [0.002886, 0.004282] | 15.616 [5.154, 25.964] |
| unet | common_support | 0.028849 [0.023391, 0.034713] | 17.765 [7.817, 27.768] |
| nn | full_grid | 0.002695 [0.002070, 0.003379] | -16.167 [-23.724, -9.293] |
| nn | common_support | 0.021385 [0.016121, 0.026997] | -14.867 [-22.012, -8.366] |
| fusion | full_grid | 0.002448 [0.001879, 0.003061] | -9.852 [-17.616, -2.697] |
| fusion | common_support | 0.019571 [0.014689, 0.024747] | -8.128 [-15.409, -1.348] |

Fusion has the lowest descriptive Brier mean in both domains, but no paired Brier contrast was returned and no recalibration benefit was tested. Full-grid background and structural zeros make small overall Brier values misleading if read alone. Full-grid positive-class Brier is tree 0.7711, U-Net 0.6908, nnU-Net 0.7941 and fusion 0.7598 (valid n=98); corresponding negative-class values are 0.000498, 0.001641, 0.000586 and 0.000382 (n=99). Positive-class valid n drops to 97 on common support; undefined classes were retained, not assigned zero. Both class contributions and their intervals remain in each `patient_first.metrics` record.

The reliability curves support score–event mismatch on this cohort. For example, in the prespecified common-support [0.9,1] bin, mean predicted/observed fractions are tree 0.9308/0.5489 (45 occupied patients), U-Net 0.9444/0.4627 (50), nnU-Net 0.9690/0.4105 (88), and fusion 0.9317/0.7942 (33). These are equal-patient averages within occupied bins, not pooled-voxel incidence or matched patient subsets across methods. All bins, including lower-score underprediction, remain in the source. High-score overprediction can coexist with whole-volume underprediction when much true tissue receives low scores. No outer-training prevalence comparator is available; favorable Brier, threshold behavior or this audit does not establish clinical calibration or justify promoting a fitted recalibrator.

**4. Centre and coverage.** `coverage.json` reports known-centre n=0, unknown n=99, centre-balanced result=null, interaction=null and zero matched normalization pairs. Those are unavailable results, not negative centre or normalization findings. The computational-support proxy—fraction of target-grid axis-2 slices containing tissue support—has mean 0.5838 [0.5679, 0.6003], median 0.5974. All 99 patients are below 0.9; the ≥0.9 group is empty with no metric estimates. Hence no between-stratum sensitivity is identified. The low-coverage fusion–tree contrast simply repeats the whole-cohort own-volume contrast. Outside-support truth volume averages 2.1495 [1.4082, 2.9822] ml, median 0.264; this is an outcome-dependent description, not the grouping variable or proof of inadequate anatomical acquisition coverage. Historical 67/31/1 centre counts cannot supply the missing mapping.

**5. Admission availability.** `availability.json` reports five dependency rows, including two unresolved upstream dependencies. Tree/U-Net cache and support provenance is UNKNOWN: consuming code is present but generating source and annotation timing are absent. nnU-Net CT/maps/CTA is ADMISSION_INTENDED_NOT_VERIFIED because original channel preparation/acquisition timing is missing. Follow-up `lesion_full` is EVALUATION_ONLY; the inspected code uses it for metrics and actual-size descriptions, not score ordering or routing. The router uses predicted volume only but inherits upstream uncertainty. Clinical scores, reperfusion and follow-up MRI input families are NOT_USED by this diagnostic program. These are desk/dataflow findings, partly fixed in the submitted audit, not newly measured acquisition timestamps. Annotation assistance alone proves neither outcome leakage nor admission availability. The prospective admission-only claim remains unverified.

**Uncertainty and prior evidence.** These are exploratory results from saved split101/training realization1 on 99 repeatedly exposed development patients, retaining the earlier 69/30 exposure history. The supplied 2,000 patient-bootstrap percentile intervals (seed0) condition on saved fitted models; they omit recipe selection, overlapping training, retraining variability and population transfer. One primary contrast was frozen; other comparisons are descriptive with no multiplicity-adjusted confirmation. Patients, not voxels/components/folds, are the resampling units. Endpoint-specific valid denominators and paired complete observations are used. Fewer than three valid patients yields counts only. No result establishes causality, clinical utility, novelty, an untouched evaluation, or the efficacy of specialists.

The external r4 notebook remains distinct: original SHA256 `6432e7d31fa50274320fdc31759c698908a649dc48ab6e9928cbbbe18ee265e6`, selected source/output view `e69a664e081ad1770454c6ce453ff4ddad3b16d2876f889ca89f8f876bb1d72b` (inspected cells4/6). Its saved shared-miss fraction 0.671 and Dice correlation 0.810 are historical observations, not recomputed diagnostics or independent replication. Its warning that meta-training predictions arose from models trained partly on scored-fold patients remains material. Accepted directions `bf6e4ffab3f54c77da4e9aa97f764074a4496dfdbc2253445d17d2e0d5d86138` retain the own-volume fusion detection penalty and union volume tradeoff. Stocktake `26abd688a46f9677af9a572fcdbe0958d711d8fe1b8ea9444ae8cb87a8f563c0` retains no calibration promotion and inconclusive cached-CNN evidence. The new placement result narrows one uncertainty; it does not erase those contrary observations. The overlapping aggregate archive is not another experimental replication, and its identity-only validation is not this execution's result evidence.

**Failures and current finding status.** Exact preserved finding records `evidence/2fe1ce22f30264d92f1cc03b81f0940c78684000c27ce9353fdae1f586eb12bf-finding.json` and `evidence/815367d0ad9b7109848ba3bc866b0cad30e775b221f0bedde545cb7e8a7f6380-finding.json` retain both original REVISE judgments. F1 concerned failed synthetic tests, F2 the environment mismatch, and F3 inaccurate receipt-availability wording. The first recorded suite had one error in ten tests; the next had one failure in ten, caused by a blanket file-open mock intercepting dependency metadata. The v4 correction narrowed that guard, retained corrected pins and preserved the failed receipts as author-time facts. Current synthetic receipt `a6dedf3014d3ed6b004e7d373caf2abb3973feacddb6d8dc94232250769584ec` reports 10/10 PASS, zero errors/failures, exit0, no patient execution. Both exact records include the later independent APPROVE closure, SHA256 `8b3ba0c8ae317fd7d4db8839cc3ddf16638aacc051df1a1d44880dc722cace6a`, closing F1/F2/F3. They are not current blockers. Historical open wording in the frozen specification and returned limitations records its original time. None of these tests, corrections or closures establishes efficacy; the actual result basis is the bound return described above. No missing declared result or failed patient attempt is reported in this selected return; the earlier synthetic failures are not negative scientific results.

**Evidence availability and omissions.** No per-patient evidence was used in this model interpretation: the registered `per_patient_material` lists are empty, so there is no per-patient inclusion reason to cite. Patient-level arrays and tables stayed outside this workspace; only aggregate outputs and selected code/provenance were inspected. The registry SHA256 is `76cee68de3a172004ca6a3a3de8d2771928a82294ae157e846d44fc786d9e893`; navigation is `evidence/a9c6c6fb45db62c193c4d487504cc862d8f83a8bf921051036b00e8902a5a1d9-private-index.json`.

The original omission manifests remain unchanged: `evidence/0e4b6b24ce24041329d47fa9ea7ac420223d185f51a3e50d50142739f977d911-omissions.json` retains notebook cell0–8 metadata/type, output metadata/type for cell4/output0, cell6/output0 and cell8/outputs0–2, JavaScript for cell8/outputs1–2, and notebook metadata/format as opaque metadata or rendered duplicates preserved operator-only. `evidence/5a52ab34051166bc70aa9173f114034eca6b93045615dd92e5c2876878dee56c-omissions.json` retains `sprint13a_precision_recall.png` and `sprint13a_dice_tree_vs_nnunet.png` as opaque PNGs withheld by the UTF-8 route. No omitted unit was interpreted. Missing centre mappings, normalization repeats, outer-training prevalence, reader plans, feature generators and timing provenance remain missing. Historical unavailable onboarding/deployment originals were not used to infer scientific results.

**Original output identities.** Let R denote `current/runs/1ed7333ef01540157462eb45ff63c3023705b752a8243f91b3ee21c0b68ee4fa/results/`. Each linked evidence file is the unchanged staged original identified by its full SHA256. Numerical citations above refer to the corresponding R/diagnostics file and JSON keys. All returned fields and contrary contrasts remain available there.

| Original file under R | SHA256 | Staged original |
|---|---|---|
| diagnostics/integrity.json | `97e936cf17ffe02acfa786438ebea1308fa1c186717236acebcdb2bb1abcc69b` | [integrity.json](evidence/97e936cf17ffe02acfa786438ebea1308fa1c186717236acebcdb2bb1abcc69b-result_tables.txt) |
| diagnostics/placement.json | `e5569c84f299539deb1362e212c6aceabe62068bdbaf3a2ccab28327640ced56` | [placement.json](evidence/e5569c84f299539deb1362e212c6aceabe62068bdbaf3a2ccab28327640ced56-result_tables.txt) |
| diagnostics/components.json | `fafdab70bde096e34a6932cafb5fb0a414bc61fdd4e001138ac2ef890efc69e7` | [components.json](evidence/fafdab70bde096e34a6932cafb5fb0a414bc61fdd4e001138ac2ef890efc69e7-result_tables.txt) |
| diagnostics/calibration.json | `7b3d7d66e29b97be8945c449daa44850b874efe6ee3da8003414d8c1142d7b94` | [calibration.json](evidence/7b3d7d66e29b97be8945c449daa44850b874efe6ee3da8003414d8c1142d7b94-result_tables.txt) |
| diagnostics/coverage.json | `d20b391ae0eca0242c2d701848e8e188c74cbc702ac5b6d3383daeb82e66892a` | [coverage.json](evidence/d20b391ae0eca0242c2d701848e8e188c74cbc702ac5b6d3383daeb82e66892a-result_tables.txt) |
| diagnostics/availability.json | `a618bf8f5918d707aaf96a692db9c6656353f55399ad26f26b121a3886f601a1` | [availability.json](evidence/a618bf8f5918d707aaf96a692db9c6656353f55399ad26f26b121a3886f601a1-result_tables.txt) |
| diagnostics/limitations.md | `bc67b55bcad8121e364546d62fca9c18636dd420454c0b6258beaf3d022633c2` | [limitations.md](evidence/bc67b55bcad8121e364546d62fca9c18636dd420454c0b6258beaf3d022633c2-result_tables.txt) |
| diagnostics/validation.json | `6068f12dbd653c29a45dff3088190427b50d08844544f29e6dbfc5895db5ae6b` | [validation.json](evidence/6068f12dbd653c29a45dff3088190427b50d08844544f29e6dbfc5895db5ae6b-validation_result.txt) |
| diagnostics-execution-receipt.json | `6581eb31fe6b84b5733ded4c1706a86a96610fc22205de83a03e0551e7c3dbec` | selected record in prompt.md |
| diagnostics-execution-manifest.json | `fe14b148cf5dce32a67190ddb9aa01df42e640ccefe3d23790fda324d60561bc` | selected record in prompt.md |
| diagnostics-package-manifest.json | `cdd62ab96713acc400480c21bbf7386c65b1cc117b27c4325e68d9f3ab788626` | [package manifest](evidence/cdd62ab96713acc400480c21bbf7386c65b1cc117b27c4325e68d9f3ab788626-package_manifest.txt) |

**Next scientific decision.** Propose stopping the item6 diagnostic branch here, without promoting the frozen router or moving to specialist training on this evidence. The fixed-amount question has a useful positive answer, while the router has no active branch, small-component recovery remains poor and prospective input provenance is unresolved. This stop concerns progression from this diagnostic package; it is not a claim that fusion, admission imaging or future specialists cannot improve prediction. The charter asks for credible follow-up infarct prediction from information available by completion of admission CT; these results do not yet support that stronger prospective claim.
