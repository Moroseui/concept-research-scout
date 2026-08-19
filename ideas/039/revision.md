# Revision — idea 039

## Outcome

The card now asks one scoped question: in one frozen multichannel ISLES'24 infarct surrogate, does experimentally increasing local central-volume residual magnitude attenuate response to an otherwise identical, identity-consistent perfusion worsening at the same site?

The revision adopts the debate's final role-disjoint, residual-preserving factorial as the only confirmatory instrument. No code, array inspection, model training, or image editing was performed.

## Material changes

1. **Preserved and narrowed the claim.** `deliverable_original` records the original sentence verbatim. The revised deliverable is restricted to observable response modulation in one surrogate on tested support. It no longer calls that surrogate “the final-infarct model” or asserts an internal confidence computation.

2. **Removed projection-versus-tangent testing as confirmation.** It can show directional off-manifold dependence but cannot show modulation of trust. It is not load-bearing in the revised experiment.

3. **Removed observational high-versus-low residual comparisons.** Natural sites differ in channel values and receptive-field context. Residual is now set high or low at the same site.

4. **Made the evidence factor residual-preserving.** A CBF-only worsening changes signed residual. The revised edit lowers CBF and compensates through CBV or MTT so signed residual remains at its preregistered set-point.

5. **Separated channel roles.** Arm A sets residual through CBV and compensates through MTT; arm B sets residual through MTT and compensates through CBV. Agreement across arms is required.

6. **Added exact cell-validity rules.** Every cell must preserve signed residual within a frozen tolerance, retain sign, avoid zero crossing and clipping/range violations, and pass a realism gate on the complete multichannel edit. Invalid cells are not negative results.

7. **Added discriminating controls.** Compensator-only, zero-dose, and off-site shams are required. The interaction must agree across swapped roles and residual-sign strata after frozen sham treatment. The sign test applies only to residual-setting.

8. **Sharpened Stage 0.** Before model work, array inspection must test stored MTT against CBV/CBF, quantify rounding and quantization, define common support and clipping, test residual stability under two masks, and count sites with three-channel headroom. An algebraic, quantization-only, artifact-dominated, or underpopulated residual kills inference.

9. **Preserved a useful Stage 0 negative.** If released MTT is effectively determined by released CBV/CBF, that is a dataset-composition result. It cannot support model use, but should be retained as a dataset-quality finding.

10. **Scoped the model honestly.** No released winner checkpoint is verified. The test concerns one frozen self-trained surrogate, gated on held-out performance and reliance on at least two linked maps. Model-family generalization is deferred.

11. **Declared resource burden.** The release is a single approximately 99 GB archive. Feasibility must name storage, split governance, eligible-site and edit counts, and GPU budget before inference.

12. **Strengthened null semantics.** A null is decisive only after powered inventory, model performance and channel reliance, exact set-points, realistic cells, and detectable sham sensitivity. It rejects the scoped functional modulation, not all models or explicit uncertainty computation.

13. **Added charter-required verified facts.** The card records modalities, the later paper's realized 149/96 split, follow-up-DWI/DeepISLES masks with neuroradiologist-supervised correction, official Dice and absolute lesion-volume-difference metrics, license, access form, and primary-source identifiers. Voxel semantics remain unverified.

14. **Updated scores.** Identifiability is 3 pending independent review. Feasibility is 2; data and evaluation readiness are 3. Interest is 4, prior legwork 3, clarity 4, and the recalculated priority score is 3.25.

15. **Removed unsupported wording.** The pitch says maps may disagree, identifies a surrogate, distinguishes an interaction null from a dataset kill, and makes no novelty claim beyond a limited-search gap.

## Prohibited conclusions

A positive result would not show explicit internal residual computation, calibrated uncertainty, why maps disagree, clinical benefit, challenge-winner behavior, transport across software, or model-family generalization. Plain single-channel CBF response is outside this residual-preserving factorial.

## Next gate

Before feasibility or model work advances, an independent review must algebraically inspect all four cells in both role assignments and decide whether a practically plausible residual-blind multichannel response can satisfy the carrier, sign, sham, and set-point conjunction. Direct released-array inspection is separately necessary. Neither was completed here.

```json
{"claim_retention": "narrowed"}
```
