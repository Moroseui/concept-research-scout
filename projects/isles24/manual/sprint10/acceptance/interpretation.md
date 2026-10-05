**Question:** Did the selected Sprint10 comparison reproduce known Sprint8/9 results, and what do those results support?

**Evidence:** The supplied validation reports `VALID`, no differences, 99 development cases, no training and `scientific_acceptance: false`. Saved aggregate results show tree D Dice 0.206 versus baseline U-Net 0.204; their paired difference is −0.002 (exploratory 95% interval −0.019 to +0.014). [V; A]

**Limitations:** External records are not new efficacy evidence. Detailed validation covers five CSVs; two required JSON comparisons and package/receipt evidence are absent. Development exposure, annotation-assisted features and locked evaluation limit inference.

**Next decision:** **PROPOSAL_ONLY** — propose opposing review and reconciliation of missing evidence before acceptance. No follow-up, amendment or ratification is authorized.

Evidence:

- **N:** [selected notebook source](evidence/e2f6d75d5d2b213594c8a1b29b89c32b79f3813a474937888b53185c88d1b224-notebook_source.txt), inspected through its final export. Citations name the relevant functions/sections. This flattened source is not the original notebook serialization.
- **H:** [historical saved outputs](evidence/6faa89dc1ee2ffdcdc5ffbab55a514f84908900353a114fb09e8e552cf39368e-result_tables.txt), cells 2, 4, 5, 7, 9 and 11.
- **A:** [collected aggregate tables](evidence/4fb56eeab814508840a4481ed87d8ef3683bc5412d4dd195041473bff7b7dc5d-result_tables.txt), sections `summary_by_recipe.csv` and `paired_contrasts.csv`.
- **E, S, V:** `current/execution.json`, `current/SPEC-1.md` and `current/validation.json`, inspected as embedded artifacts in [prompt.md](prompt.md), lines 791–792, 917–992 and 995–996. Logical paths are not standalone workspace files; their supplied full hashes remain in that record.

Execution, input integrity and byte equality are attributed to inspected records, not independently verified from hashes. No patient payload, private original, experiment, model client, literature search or remote service was accessed.

Selected run: `sprint10-stepd-a9123b81e3ef32ee`. E's source/spec/notebook-code bindings and V's manifest binding remain unchanged and distinct from the original repository pin. [E; V; N, configuration]

Preserve every configuration/private-input pin in N and S: tree `run-875c56c278`, FULL-protocol network `run-0a60362503`, existing cache, feature settings, original source reference, split/exclusion hashes and count 1, code version and map settings. Membership remains private; `assert len(CASES) == 99` remains intact. The 25 final-evaluation and 24 reserve patients remain locked. Preserve P001, task921, earlier attempts, partitions and original results; these Sprint results do not become P001 outcomes. [N, configuration/membership; S; supplied obligations]

N defines training helpers but does not call them on the comparison path. Its wrapper checks identities, copies seven baseline files before comparison, isolates new outputs and exports originals/new files with source/spec/notebook/private-input bindings. Source inspection does not prove execution. The prescribed route remains manual Colab CPU, existing cache/dependencies and completed Sprint8/9 runs, zero fitting, paid resources or discretionary retries. [N, capture/export; S]

The actual validation status is present, not missing: **V reports VALID, provisional false, differences [], training_performed false, scientific_acceptance false**. Its five detailed entries report identical baseline/actual hashes and zero differences:

| Artifact | Reported rows |
|---|---:|
| all_percase.csv | 6732 |
| completion.csv | 150 |
| matched_amount_status.csv | 50 |
| paired_contrasts.csv | 12 |
| summary_by_recipe.csv | 22 |

H reports 100/100 fold tables complete and 50/50 score combinations paired, producing 990 matched-amount rows. Thus 150 completion rows include fold tables plus score files; they are not 150 folds. H cell 4 reports all hard compatibility checks passing, ten identical full partition dictionaries and matching parsed clinical digest, fields and header mapping. Cell 5 explicitly reports two Sprint8 execution records and its active arm list; missing records were not inferred from output size. [H, cells 4–9; V]

Difference accounting is bounded to the supplied evidence. V lists no CSV differences, so no numerical or formatting discrepancy is demonstrated. Preserve atol 1e-10, rtol 1e-09, exact row/column order, exact strings/counts/formatted intervals, 2000 bootstrap resamples and seed 0. Only `utc`, `code_version`, `fingerprint`, `run_identity` and the original/new comparison-output directory prefix may differ. Permitted changes would reflect capture time, code identity, predecessor/private-reference binding and isolated output location; these are explanations, not observed before/after differences. Predecessor paths, cache, membership, partitions and clinical inputs cannot change under those allowances. [E; V; N]

V has no detailed entries for `comparison_reference.json` or `compatibility_report.json`, although E pins both baseline hashes. Actual JSONs/comparisons, package manifest, started marker, execution receipt, original CSV bytes and validator implementation are absent. V's VALID is reported faithfully, but the full seven-file contract and actual JSON differences cannot be independently verified here. Missing validation detail remains a limitation, not a pass or evidence that a mismatch occurred. S's earlier statement that no validation return was supplied describes the earlier specification stage; V now supplies one. S's referenced data-contract status is not independently supplied or established here. No missing record is reconstructed or sought privately.

Measured performance below is transcribed from A, not newly calculated. All rows summarize 99 patients; repeats are averaged within patient. D and baseline U-Net recipes have four repeats; clinical network recipes have two.

| Recipe | Mean Dice (exploratory 95% interval) | Lesion-wise F1 | Median patient-mean absolute volume error, ml |
|---|---|---:|---:|
| D tree | 0.206 (0.169 to 0.247) | 0.112 | 16.36 |
| U_base smoothed | 0.204 (0.164 to 0.244) | 0.094 | 28.57 |
| U_base at D amount | 0.196 (0.158 to 0.235) | 0.098 | 16.36 |
| U baseline-clinical broadcast, smoothed | 0.204 (0.165 to 0.249) | 0.084 | 33.47 |
| U baseline-clinical FiLM, smoothed | 0.197 (0.157 to 0.240) | 0.091 | 17.26 |
| U post-intervention broadcast, smoothed | 0.220 (0.180 to 0.266) | 0.115 | 19.99 |

A preserves all 22 recipes. All 12 contrasts follow, first minus second; display rounding only. Volume differences are medians of patient-mean paired absolute-error differences, not differences between descriptive medians. [A, both sections]

| Contrast | Matched observations | Dice difference (95% interval) | Volume-error difference, ml (95% interval) |
|---|---:|---|---|
| U_base smoothed − D | 396 | −0.002 (−0.019 to +0.014) | +11.1 (+6.9 to +14.0) |
| U_base at D amount − D | 396 | −0.010 (−0.023 to +0.003) | 0.0 (0.0 to 0.0) |
| U_base at D amount − U_base smoothed | 396 | −0.007 (−0.020 to +0.003) | −11.1 (−14.0 to −6.1) |
| U baseline-clinical broadcast at D amount − D | 198 | −0.008 (−0.022 to +0.006) | 0.0 (0.0 to 0.0) |
| U baseline-clinical FiLM at D amount − D | 198 | −0.013 (−0.029 to +0.003) | 0.0 (0.0 to 0.0) |
| U post-intervention at D amount − D | 198 | +0.003 (−0.010 to +0.017) | 0.0 (0.0 to 0.0) |
| F baseline clinical − D | 396 | −0.018 (−0.037 to +0.002) | −2.0 (−4.4 to +2.8) |
| G post-intervention − D | 396 | −0.001 (−0.010 to +0.008) | −1.6 (−2.9 to −0.4) |
| K volume-only recalibration − D | 396 | −0.029 (−0.040 to −0.018) | −4.7 (−6.7 to −2.5) |
| I clinical amount − K | 396 | −0.002 (−0.009 to +0.005) | −0.1 (−0.7 to +1.1) |
| U baseline-clinical smoothed − F | 198 | +0.015 (−0.007 to +0.040) | +17.9 (+9.2 to +25.0) |
| U post-intervention smoothed − G | 198 | +0.015 (−0.003 to +0.034) | +6.9 (+3.8 to +8.6) |

Source-supported interpretation: the baseline U-Net shows no demonstrated Dice improvement over D here, and has larger paired volume error. This establishes neither equivalence nor absence of predictive information. At D's predicted amount, baseline U-Net ranking provides no demonstrated placement advantage. Identical volume error at matched amount is expected by construction, not independent predictive success. K improves volume error while reducing Dice, illustrating an endpoint tradeoff. Clinical-network versus clinical-tree contrasts do not establish incremental clinical benefit versus U_base. No such new contrast is added.

D precision/recall are 0.257/0.262 versus U_base 0.214/0.341; the latter trades precision for recall. D versus U_base feature-mask AUROC is 0.865 versus 0.844, and average precision 0.252 versus 0.232. Ranking metrics have 97 valid patients, recall/ASD 98, and precision/specificity 99; undefined domains must not be zero-filled. D Dice is 0.028 for the 29 lesions below 5 ml versus 0.280 for the 70 at least 5 ml. Dice equals voxel F1 and is distinct from lesion-wise F1. Predictions stay inside the feature mask, while Dice and volume scores use complete lesion truth. [A, D/U_base rows; N, patient_scores/fold_check]

Uncertainty remains exploratory. N matches shuffle/fold/seed/patient, averages differences within patient and bootstraps patients. Its single `default_rng(0)` stream consumes descriptive-summary draws first, then Dice-mean, volume-median and lesion-F1-mean draws for each contrast, 2000 each, with 2.5/97.5 percentiles. Algorithm, order and formatting remain unchanged. These intervals do not quantify all training, selection or population uncertainty; repeated folds are not independent patients. Two baseline seeds show observed sensitivity, not a reliable training-variance estimate; clinical network arms use seed 1 only. Multiple exploratory contrasts do not become confirmatory discoveries because an interval excludes zero. [N, summary/contrast section; H, cell 5; S]

Preserve the known 69/30 prior development-outcome exposure across the 99, partly annotation-assisted cached representation, mask exclusions and unequal repeats. This compares whole pipelines, not architecture or spatial context alone, and is not a source-image network validation. Admission clinical fields remain distinct from achieved reperfusion/mTICI and its recordedness; post-intervention rows cannot support admission-time, causal treatment or treatment-plan claims. Historical review reports 68 recorded grades and 31 missing, mostly high recorded grades; that remains attributed background, not a newly verified clinical census. Field/digest agreement does not establish correct parsing or timing. The locked 25/24 have no evaluation evidence here. Maps use outcome-based lesion-size selection and maximal-lesion slices; the save message is not an inspected image or independent evaluation. [S; supplied S9-R4-LIMIT-02 and exposure obligations; N, maps; H, cell 11]

N addresses S10-R4-01–04 in source, but no exact closure receipts are supplied. Sprint9 checkpoint/resume, parser, reporting and override findings retain their scope; no repair/retraining is proposed. Pandas/UTC warnings remain advisories. Formal047 and implementation review047 remain distinct.

Propose retaining reported reproduction, with missing acceptance details unresolved. Full acceptance is undecided. Review has at most two rounds; no reviewer verdict is authored here. REVISE is reserved for a concrete blocker with `BLOCKER[category]` using only test-set/leakage, code/spec mismatch, metric/statistic, privacy/secret, budget, or execution authority/provenance. Other concerns remain advisories; APPROVE cannot conceal an unresolved blocker. Any demonstrated nonpermitted difference blocks acceptance. After two rounds retain unresolved findings. No rerun, scientific change, dependent execution, remote write, deployment, merge, spending, adoption or ratification is authorized.
