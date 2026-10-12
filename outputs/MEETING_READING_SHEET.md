# Meeting reading sheet

Updated 12 October 2026. The three summaries below are verbatim from independently accepted scientific interpretations. This is an editorial reading sheet, not a new analysis or joint scientific conclusion.

## Placement at fixed amount

Does combining the tree and nnU-Net improve where infarct tissue is predicted when predicted volume is held constant? Yes, within these 99 development patients: mean Dice rose from 0.2063 to 0.2467, a paired gain of 0.0404 (95% patient-bootstrap interval 0.0280–0.0542). This supports a placement benefit for the frozen rule, but not clinical effectiveness. The original own-volume fusion still lost lesion-detection F1 and produced many unmatched components. Small-infarct performance remained poor. The fixed size router selected the tree for every patient, so it added nothing. Calibration showed substantial score–event mismatch. Centre effects and admission availability remain unresolved; all patients also fell into one coverage stratum. Results reuse exposed development patients and saved fitted models, so intervals omit training, selection and transfer uncertainty. Stop this diagnostic branch without promoting the router or specialist training from these results.

[Accepted source](item6/interpretation.md).

## Ranking versus predicted amount

Does fusion help by placing predicted tissue better, estimating its amount better, or both? Across 99 exposed development patients, fusion improved placement over tree ranking at every fixed amount. At fusion ranking, replacing tree amount with nnU-Net amount reduced mean Dice by 0.0366 (95% interval −0.0555 to −0.0174). Fusion amount changed Dice by only +0.0023 (−0.0061 to +0.0108), while reducing mean absolute volume error by 4.31 ml. Mean Dice with fusion ranking and fusion amount was 0.2491; below 5 ml true infarct volume it was only 0.0611. All 891 allocations were feasible. These saved-fit diagnostics do not establish clinical benefit, anatomical explanations or untouched-test performance. Intervals exclude training and selection uncertainty; admission provenance remains unverified.

[Accepted source](idea2_fixed3x3/REPORT.md).

## Smoothing and fragmentation

Does removing smoothing recover small infarct components while keeping predicted volume fixed? In 99 exposed development patients, the gain was tiny and uncertain: mean small-component recall rose from 0.002688 to 0.004910 among 93 eligible patients; the paired change was +0.002222 (descriptive 95% interval 0 to 0.006237). Mean Dice fell from 0.206306 to 0.184822, while unmatched predicted components rose from 2.707 to 71.202 per patient. Volume was identical in both arms. Thus, removing smoothing did not demonstrate a useful rescue of small components and produced much more fragmented predictions under the fixed measurement rules. These are exploratory results from one saved split and seed, not evidence about anatomical correctness or clinical usefulness. The five returned files validate consistently; the current review text and underlying execution logs are not available for direct inspection. Stop this bounded interpretation and return it to the operator.

[Accepted source](SMOOTHING_RESULTS_20261012.md).

## Current experiments and visual review

Pnormct is running in Partho's Colab session. Multiwin awaits the returned real-trainer check before full delivery. Pnorm_v2 authoring is complete; scientific review is running with the synthetic failure evidence. These are work states, not performance results.

The [private visual-review plan](MEETING_CASE_REVIEW_PLAN.md) fixes case selection before image inspection. No cases have been selected and no image panels are ready. Follow-up MRI and clinical-source provenance remain unresolved. The first visual deliverable is an author-written, reviewed selector/renderer tested on synthetic data; real panels require the mandatory private assets and geometry checks.
