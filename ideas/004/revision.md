# Revision of idea 004

## Revised question

Across geometry-matched alternative reconstructions of the same CT-RATE acquisition, how much do the frozen ClassFine abnormality scores change?

This revision implements the converged debate and the completed Stage 0 findings. It retains one experiment: compare a frozen model with itself across 425 strict, same-acquisition, geometry-matched reconstruction pairs. It does not retain the separate benchmark-precision study.

## Material changes

1. **Narrowed the question to paired score sensitivity.** The prior card joined reconstruction repeatability to a clustered benchmark audit. The latter needs labels, a separately defined weighting estimand, and additional inference. It is now excluded from the primary question. Reconstruction-swap rank summaries may be descriptive only.

2. **Renamed the study.** “Free test-retest” was removed because no acquisition was repeated. The study is now a within-acquisition reconstruction-sensitivity audit.

3. **Used the completed Stage 0 evidence.** The card now records 3,039 validation volumes, 1,564 scans, 1,304 patients, 1,432 multi-reconstruction scans, and 425 strict geometry-matched pairs. It also records the dominant contrast counts and the overwhelmingly Siemens composition. These replace the old inferred validation structure.

4. **Replaced the keystone.** Pair existence is no longer the load-bearing unknown; it was directly confirmed. The real keystone is whether the exact published ClassFine checkpoint is obtainable and provenance-verifiable. The inspected official locations contained inference code but no released per-volume scores or checkpoint assets. `keystone_status` is therefore `NOT_INSPECTED`, and feasibility and novelty confidence are capped at 3.

5. **Removed the label-only design-effect claim.** Duplicate labels and cluster sizes cannot determine AUROC variance or confidence-interval inflation. Stage 0 is treated only as the completed linkage and feasibility audit. No primary endpoint uses CT-RATE labels.

6. **Replaced ICC as the primary statistic.** A pooled ICC can conceal large borderline score changes and is ill-suited to heterogeneous reconstruction contrasts. The revised primary endpoints are paired score differences and an upper bound on absolute change, stratified by named reconstruction contrast and reported on probability and logit scales. Patient is the outer bootstrap unit.

7. **Removed unsupported thresholds and numerical reassurance criteria.** The old `ICC > 0.95` and “low-single-digit” flip criteria had no external justification. Threshold flips are no longer primary. A decisive equivalence result now requires an externally justified margin fixed before inspecting the paired scores.

8. **Removed the attenuation-bound argument.** Within-acquisition reconstruction agreement is not total measurement reliability and cannot impose a general ceiling on correlations with external outcomes. The cross-domain architecture built around classical test theory was deleted.

9. **Corrected the causal scope.** The primary cohort is restricted to pairs matched on array shape, spacing, slope/intercept, position, and acquisition parameters so the deterministic preprocessing function is held fixed. The permitted claim is sensitivity to reconstruction-dependent image content under the observed contrasts. The card does not claim that a specific kernel, anatomical feature, or frequency band caused the response.

10. **Made X explicit and independently measurable.** X is reconstruction-dependent spatial-frequency content, measurable from the images through frequency-energy or noise-power-spectrum statistics and the recorded kernel contrast without human annotation. The present experiment reaches rung 1 only; naming a more specific human-legible image property would require an independent measurement or intervention.

11. **Made vendor/site limits explicit.** Because 462 of 464 audited volumes were Siemens, scanner/vendor is not a within-pair explanation but is an unresolved effect modifier. No cross-vendor or broad site-general claim is allowed.

12. **Preserved a meaningful negative.** A powered confidence bound wholly inside a prespecified external margin would decisively weaken material reconstruction sensitivity for the observed contrasts and checkpoint. Mere non-significance remains sensitivity-limited and is not presented as reassurance.

13. **Added explicit stop and identity rules.** If the exact checkpoint cannot be obtained, the idea stops. Retraining or substituting another model would change the claim and must become a new candidate rather than a quiet repair.

14. **Reduced scores and priority.** Medical relevance and interest were moderated, feasibility and novelty were capped at 3, negative-result value was reduced from 5 to 4, and the weighted priority score changed from 4.10 to 3.55.

## What was deliberately removed

- test-retest terminology;
- label ICC and label-only design effects;
- pooled ICC as the headline endpoint;
- audit-pair-derived thresholds and flip-rate targets;
- benchmark confidence-interval correction as a co-primary arm;
- claims of concept validity, clinical actionability, or general reliability;
- the classical-test-theory attenuation ceiling;
- the assertion that an identical-file rerun rules out preprocessing;
- broad novelty claims about reconstruction sensitivity.

## Current gate

Before a feasibility memo or probe contract, inspect the actual checkpoint artifact, configuration, checksum, and license. The existence of code and clean image pairs is not a substitute for that asset.
