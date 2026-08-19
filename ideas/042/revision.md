# Revision — idea 042

## Outcome

The card now asks one bounded question: on a preregistered common-support subset, does one frozen raw-temporal final-infarct surrogate respond consistently across two realistic low-dose operators that reduce delay-independent dispersion while preserving arrival time, area, and peak height?

This narrows the original model-use claim and removes unsupported collateral attribution. No code, archive inspection, model training, or probe work was performed.

## Material changes

1. **Recorded and narrowed the claim.** `deliverable_original` preserves the original sentence verbatim. The revised deliverable is limited to one surrogate, one low-dose common-support regime, and operator-invariant post-alignment shape. It does not attribute that signal to collateral anatomy.

2. **Reduced the card to one confirmatory question.** Capture, association, manifold, support, performance, and power analyses are gates. The sole confirmatory endpoint is operator-concordant response to low-dose dispersion reduction relative to matched delay.

3. **Implemented the common-support repair.** Peak-preserving edits are confirmatory only where arrival, area, and peak can remain fixed with headroom above the boxcar bound. Confirmatory 50% and 75% doses, the dispersion-minus-peak subtraction, and its additivity assumption are removed.

4. **Made alternative-operator invariance load-bearing.** One edit licenses only operator-specific sensitivity. Two independently specified operators must reach matched dispersion-coordinate changes, pass identical gates, and produce signed, dose-concordant responses.

5. **Made the disputed curve-family premise testable.** Stage 0 compares prespecified one- and multi-dimensional descriptions after conditioning on arrival, area, and peak. Continuation requires held-out reconstruction and descriptor residuals supporting an effectively one-dimensional monotonic trajectory over the authorized range. This operationalizes, but does not prove, transport physiology.

6. **Expanded curve characterization.** Second moment remains primary; skewness, tail fraction, kurtosis, maximum slopes, and spectral energy are mandatory. Operators and descriptors are preregistered and all changes published. The card does not claim the model computes any formula.

7. **Separated association from use.** A model-blind within-delay outcome test is a premise gate, not evidence of use. Use requires paired intervention on untouched cases.

8. **Added capture and timing gates.** The 20-case screen retains the pre-arrival, peak, washout, and ICC thresholds and adds exact-series provenance, timing inspection, and frame-decimation stability. One-frame-per-second resampling is not treated as proof of full bolus capture.

9. **Removed unnecessary architecture.** No shallow architecture, 12-case set, or unspecified “same model as c07” remains. Feasibility must freeze one minimally adequate surrogate, split, performance gate, power analysis, margins, and case counts before outputs.

10. **Corrected dependency and cost.** No qualifying public checkpoint is verified. The study may depend on idea 041 or require training. The stale 25 GB/one-session estimate becomes the inspected approximately 99 GB archive and a multi-stage, tens-of-GPU-hours estimate.

11. **Corrected closest work.** Winder is correctly attributed; Amador et al. is added as the closest interpretation neighbor; Willats et al. is added for dispersion-sensitive prediction; predecessor `isles24-scout-003-c06` is acknowledged. Full Amador inspection remains mandatory.

12. **Removed the novelty claim.** The card reports only a targeted-search gap, explicitly not proof of absence, and lowers novelty confidence.

13. **Added charter-required facts.** Modalities, cohort and split, follow-up-DWI mask production, expert correction, license/access, archive size, and all official measures are recorded with primary identifiers.

14. **Preserved a meaningful negative.** After every gate passes, an equivalence-bounded absence of operator-concordant response rejects use of the tested signal by that surrogate within S. Operator disagreement rejects the broad dispersion interpretation and records operator sensitivity. Early failures remain sensitivity-limited.

15. **Added prohibited conclusions.** No collateral physiology, unique descriptor computation, extrapolation beyond S, cross-model generalization, exclusion of preprocessing provenance, use from association, or non-use from gate failure.

16. **Rescored the design.** Identifiability, feasibility, evaluation readiness, data readiness, and novelty confidence fall because the manifold, operators, archive timing, and checkpoint are unresolved. Weighted priority is 2.95.

## Removed

The revision removes “collateral-route signal,” “changes only spread,” large confirmatory doses, peak subtraction, fixed 12-case/10-GPU-hour/25-GB promises, and any implication that a checkpoint exists. The remaining uncertainty is the original one at narrower scope: use of delay-independent dispersion-shaped information rather than delay.

```json
{"claim_retention": "narrowed"}
```
