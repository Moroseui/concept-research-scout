# Summary

Can the server CPU reproduce the completed Sprint10 comparison? The saved receipt and validation report say yes: all five CSVs match byte-for-byte, and both JSON files retain identical scientific content [R,V]. This reproduces existing results on 99 development patients without training; it adds no new efficacy evidence. Tree D achieved Dice 0.206 and the baseline U-Net 0.204. Their paired difference was −0.002 (exploratory 95% interval −0.019 to +0.014); the U-Net’s paired volume-error difference was +11.1 ml [T]. These results establish neither U-Net superiority nor equivalence. Prior outcome exposure, annotation-assisted features, restricted prediction masks and limited training seeds constrain interpretation. Original private return files were not supplied here, so equality is attributed to the saved validation. Stop this completed reproduction thread; no repeat is needed.

# Details

**Evidence inspected.** The four evidence-file SHA256 values were locally verified against their filename prefixes. Citations below distinguish original supplied files from records embedded in the stage’s saved prompt:

- [T] [Collected aggregate tables](evidence/4fb56eeab814508840a4481ed87d8ef3683bc5412d4dd195041473bff7b7dc5d-result_tables.txt), full file: `summary_by_recipe.csv` and `paired_contrasts.csv` sections.
- [O] [Historical saved notebook outputs](evidence/6faa89dc1ee2ffdcdc5ffbab55a514f84908900353a114fb09e8e552cf39368e-result_tables.txt), full file, cells 4, 5, 7, 9 and 11.
- [N] [CPU notebook source](evidence/91dc9c8fba7f5876cc61fcb02b40f7f395d4524711daad7bea253907fb6ed0f5-notebook_source.txt), configuration/capture lines 13–138 and comparison/report/return lines 682–976.
- [M] [Package manifest](evidence/1a7d85a21188a98d9c6b12d55a40ea8a8bc2466dba9eb66f97fd5ccef67f4ae5-package_manifest.txt), `data_binding`, `private_files`, `baseline_sha256`, `tolerance`, and package identities.
- [R] `current/execution-receipt.json`, embedded in [prompt.md](prompt.md) lines 849–903, declared SHA256 `b55492e5c399231478393ec5867e2acd0624be7adf6a96e1de78b055256d576d`.
- [V] `current/validation.json`, embedded in [prompt.md](prompt.md) lines 1009–1010, declared SHA256 `2efbc269198ee58b41e086ab94c1b9b21a23a022950268ff8fb26bb598a4ee49`.
- [S] `current/SPEC-1.md`, embedded in [prompt.md](prompt.md) lines 929–1006, declared SHA256 `2a29b31776e6bc983ff721d21d1e30bdbe83e11b3b525808e5a39687a0787d6e`.

**Reproduction finding.** [R,V] bind run `sprint10-cpu-3b82380564e25cf2`, source `7f781a56479ae3ae3cb272616b09ef66b2e39552`, specification identity [S], and notebook code hash `26d425e1e9193c753c8b23ef28e49a7b637443ae4ea87cf333a6831f32512055`. Locally parsing [M] and hashing its canonical sorted JSON yields `d714276043bac7f403c44f3076ad766b2f2b17346f841eae3d0e318e42a203a2`, exactly the manifest hash in [R,V]. The source-text and code-cell hashes identify different representations.

[V] reports `VALID`, no differences, `provisional=false`, `training_performed=false`, and 99 development cases. Each table has equal baseline/actual SHA256 and zero differences:

| CSV | Rows | Identical baseline/actual SHA256 |
|---|---:|---|
| completion.csv | 150 | 150231afb5fa4659e053bf6e5b6ceffa47c1460643c379467eed99c840385447 |
| matched_amount_status.csv | 50 | faa1c29ccedf3a81a0e5431ee11ee02fa5511a0b5750b6d2c277b19e916443b6 |
| summary_by_recipe.csv | 22 | 51c30fd96f55a0fcfc076351fedeea7b17d9ddbee900d4f616c22f8bdc6d1348 |
| paired_contrasts.csv | 12 | 0056c3967a43d97def92abad4af4d97c683fa2af992e87e2539bce93a57c7073 |
| all_percase.csv | 6732 | ca6a08951e2453c1ccdeab9d7513f3f63332d24179097d751913f589d19e9df9 |

Both JSON files have different raw hashes, as recorded in [R,V], but [V] reports exact scientific content and key-set checks, with zero nonpermitted differences. The only allowed metadata differences are `utc`, `code_version`, `fingerprint`, and `run_identity`. Numeric output tolerance is zero.

The 99-only split is derived from the verified development cohort, not from the original mixed-membership split. [M].`data_binding` records 759 assets, cohort hash `45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86`, derived split hash `3ace11512d345b2cc0d8e78cf95b98f9f4afe45c581a1d4ab1f38c81cd3fd615`, and empty-exclusion hash `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`, count 0. Empty exclusions reflect membership that already omits the original excluded case; they do not reinstate that case. The legacy `/content/drive` input prefix is a server mount alias in [S]; the Colab mount message in [O] belongs to the historical run.

[O] reports 10 identical partitions, matching cache and clinical-input identities, 100/100 fold tables, 50/50 score archives, and 50/50 matched-amount combinations producing 990 rows. The returned completion counts and exact table matches support reproduction of that complete comparison [V]. These are completion records, not independent patients.

**Measured predictive performance.** The following retains every reported recipe [T, summary section]. All have 99 patients. “Repeats” are observations per patient averaged before summarization. Dice intervals are exploratory 95% patient-bootstrap intervals; volume error is the median patient-mean absolute error in ml. BC denotes baseline clinical broadcast, PI post-intervention broadcast, and FiLM baseline clinical conditioning.

| Recipe | Repeats | Dice (95% interval) | Lesion-wise F1 | Volume error, ml |
|---|---:|---|---:|---:|
| B natural scoresum | 4 | .177 (.143, .213) | .012 | 15.27 |
| C noslice scoresum | 4 | .183 (.149, .218) | .012 | 16.36 |
| D noslice smoothed | 4 | .206 (.169, .247) | .112 | 16.36 |
| E allvoxels smoothed | 2 | .206 (.167, .246) | .110 | 16.26 |
| F baseline clinical broadcast | 4 | .188 (.153, .225) | .092 | 11.73 |
| G post-intervention broadcast | 4 | .205 (.167, .244) | .109 | 12.50 |
| H both broadcast | 4 | .194 (.159, .228) | .112 | 10.21 |
| I D amount baseline clinical | 4 | .175 (.143, .214) | .091 | 10.51 |
| J D amount both | 4 | .173 (.139, .208) | .074 | 11.08 |
| K D amount volume-only | 4 | .177 (.142, .214) | .092 | 10.21 |
| U_base at D amount | 4 | .196 (.158, .235) | .098 | 16.36 |
| U_base raw | 4 | .196 (.161, .236) | .069 | 28.57 |
| U_base smoothed | 4 | .204 (.164, .244) | .094 | 28.57 |
| U_BC at D amount | 2 | .198 (.161, .234) | .101 | 16.43 |
| U_BC raw | 2 | .195 (.155, .236) | .041 | 33.47 |
| U_BC smoothed | 2 | .204 (.165, .249) | .084 | 33.47 |
| U_PI at D amount | 2 | .209 (.169, .251) | .118 | 16.43 |
| U_PI raw | 2 | .211 (.171, .250) | .077 | 19.99 |
| U_PI smoothed | 2 | .220 (.180, .266) | .115 | 19.99 |
| U_FiLM at D amount | 2 | .193 (.156, .231) | .097 | 16.43 |
| U_FiLM raw | 2 | .193 (.154, .235) | .073 | 17.26 |
| U_FiLM smoothed | 2 | .197 (.157, .240) | .091 | 17.26 |

All 12 prespecified contrasts appear below [T, paired section]. Differences are first minus second. Each uses 99 patients; matched observations are listed separately. Negative volume-error differences favor the first arm. Smoothed U recipes are used unless “at D amount” is specified.

| Contrast | Observations | Dice difference (95% interval) | Volume-error difference, ml (95% interval) |
|---|---:|---|---|
| U_base − D | 396 | −.0021 (−.0189, .0138) | 11.076 (6.850, 13.972) |
| U_base at D amount − D | 396 | −.0096 (−.0228, .0028) | 0 (0, 0) |
| U_base at D amount − U_base | 396 | −.0074 (−.0201, .0034) | −11.076 (−14.013, −6.138) |
| U_BC at D amount − D | 198 | −.0082 (−.0225, .0055) | 0 (0, 0) |
| U_FiLM at D amount − D | 198 | −.0130 (−.0288, .0031) | 0 (0, 0) |
| U_PI at D amount − D | 198 | .0033 (−.0100, .0170) | 0 (0, 0) |
| F − D | 396 | −.0176 (−.0371, .0019) | −1.980 (−4.372, 2.806) |
| G − D | 396 | −.0009 (−.0102, .0083) | −1.596 (−2.938, −.360) |
| K − D | 396 | −.0285 (−.0402, −.0176) | −4.650 (−6.688, −2.486) |
| I − K | 396 | −.0019 (−.0091, .0048) | −.066 (−.687, 1.134) |
| U_BC − F | 198 | .0147 (−.0068, .0401) | 17.860 (9.196, 24.988) |
| U_PI − G | 198 | .0155 (−.0031, .0339) | 6.924 (3.780, 8.648) |

The baseline U-Net trades increased recall (.341 versus D’s .262) for lower precision (.214 versus .257) and larger absolute volume error. Lesion-wise F1 is .094 versus .112; the paired F1 difference is −.0186 (−.0432, .0053). Dice does not establish an improvement. At D’s predicted amount, the U-Net also shows no clear placement gain. Equal volume errors there are a construction consequence of matching predicted amount, not evidence of perfect volume prediction. Volume-only recalibration K improves volume error while reducing Dice, illustrating the competing objectives. No interval spanning zero establishes equivalence [T,N].

AUROC/AP use 97 valid patients; recall/surface distance use 98; precision/specificity use 99. Empty-prediction rates are zero throughout. D’s Dice is .028 for 29 cases below 5 ml and .280 for 70 larger cases; U_base gives .031/.275. These are descriptive strata [T].

**Uncertainty and advisories.** [N, reporting cell] matches shuffle, fold, training seed and patient, computes differences, then averages within patient. Dice and lesion-F1 contrasts average across patients; the volume contrast takes the median of patient-mean paired absolute-error differences. It is not the difference of marginal medians (28.57 − 16.36 is not the paired 11.076 ml). The single `default_rng(0)` stream supplies 2,000 bootstrap resamples per statistic, using 2.5/97.5 percentile endpoints. Patient resampling is conditional on these saved predictions, not new training or independent replication. Overlapping training sets, prior outcome exposure, and multiple exploratory contrasts limit a population or confirmatory reading. Two baseline training seeds describe sensitivity, not a reliable training-variance estimate; network clinical arms use seed 1 only [O,S].

The cohort has prior development-outcome exposure, including the recorded 69/30 history. The 25 final-evaluation and 24 reserve patients supply no evaluation evidence here. Both pipelines use partly annotation-assisted caches and mask-constrained predictions; full-lesion Dice retains missed tissue outside the mask, whereas AUROC/AP are restricted to the feature mask. Architecture, sampling, preprocessing and losses also differ, so a pipeline contrast cannot isolate spatial context. Clinical table agreement does not itself verify admission timing. Age/sex/admission NIHSS are intended baseline fields; achieved mTICI and its recording indicator are post-intervention. The largest descriptive Dice (.220 for U_PI) is therefore not an admission-only result, treatment recommendation or causal estimate. Network-versus-tree clinical contrasts do not isolate the incremental benefit of clinical information within the network [N,O,S; prompt.md, ISLES-SPRINT-EXPOSURE-01 and S9-R4-LIMIT-02–04].

The evidence supports the bounded reproduction conclusion. The raw baseline/actual private CSVs and JSONs, patient assets, executed notebook file, original package review and CPU console were not supplied as separate files. Their contents and execution checks are represented by [M,R,V], not independently revalidated here. [R] records Python 3.12.3, NumPy 2.1.3, pandas 2.2.3, SciPy 1.16.3, scikit-learn 1.6.1 and nibabel 5.4.2. CPU elapsed time, peak memory, full environment digest, cost and intervention time are unavailable; historical notebook timings are not CPU benchmarks. [V] records `scientific_acceptance=false`; STATE’s acceptance original was unavailable. Older Sprint9/Sprint10 findings remain open absent their exact resolutions; reproduction does not demonstrate upstream training recovery or resolve those findings. These are advisories, not observed output mismatches.

**Next decision.** Stop this known-case reproduction thread because the returned evidence answers its equality question. Preserve the reproduced measurements as exploratory development evidence.
