# Revision — idea 046

## Outcome

The candidate is narrowed to one finite-population question: which of the 99 observed cases contribute most to the realized band-3-minus-band-2 mean contrast?

The binary diffuse-versus-carrier verdict is removed. The dataset has no repeat measurement or independently calibrated measurement-error unit capable of supporting stable patient-carrier classification. The surviving experiment accounts for the frozen estimator exactly and makes no stability or population claim.

## Material changes

1. Added `deliverable_original` verbatim. The revised deliverable concerns numerical dominance in one realized estimator, not stable carriers or cohort diffuseness.
2. Rewrote the question around the single band-gap quantity `band 3 - band 2`, replacing two loosely coupled band analyses.
3. Defined each case contribution as `(d_band3 - d_band2) / 99` and froze every output: signed and absolute cumulative curves, top-k shares for k = 1, 5, 10, and 20, and smallest k reaching 50% and 80% of positive contribution.
4. Removed the smallest-CI-flipping subset rule because it measured proximity to loss of significance and shrinking sample size, not concentration.
5. Removed permutation calibration, the hierarchical null, inverse-count variances, spatial resampling, planted-carrier simulations, and all binary thresholds. Each lacked a replication unit matched to stable carrier status.
6. Preserved a bounded negative: a shallow ranked curve with modest fixed top-k shares rules out a few observed cases numerically accounting for most of this estimator. It does not establish biological or population diffuseness.
7. Made the clinical join optional secondary description and enumerated its variables. Deficit size must be displayed jointly with clinical outcomes.
8. Corrected acquisition: phenotype CSVs are inside the approximately 99 GB `train.7z`, not a small download. Reads are restricted to the 99 analyzed identifiers.
9. Corrected the keystone to unique finite band-2 and band-3 rows for the same 99 cases. Those rows were inspected, so status is `INSPECTED_TRUE`; phenotype completeness cannot block the primary analysis.
10. Changed search mode from C to A because this finishes an explicit parent-analysis gap and tests no speculative mechanism.
11. Tightened identifiability and prohibited conclusions around one-census arithmetic, repeatability, confounding, and transport.
12. Re-scored under the standard rubric. The weighted priority score is 4.1; descriptive scope lowers medical relevance, interest, and negative-result value.

## Claim identity

This is a narrowing, consistent with the idea-045 precedent. The subject remains the same observed reversal and the question of who numerically carries it. What is relinquished is the unsupported epistemic ceiling: stable-carrier labels and cohort diffuseness. A future stability claim requires a separately registered successor with genuine repeated or independently calibrated measurements.

```json
{"claim_retention": "narrowed"}
```
