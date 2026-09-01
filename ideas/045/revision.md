# Revision — idea 045

## Outcome

The candidate is narrowed to one already-supported analysis: test whether per-patient Q1-versus-Q4 median NCCT attenuation imbalance accounts for the opposite-signed final-infarct contrasts in flow bands 2 and 3.

The proposed viability gate and tissue-gated census are removed. The debate established that HU selection can remove outcome-bearing tissue, so a post-gate null cannot decisively reject the underlying joint-CBV/MTT association without an unavailable external bound on HU-by-outcome effect modification.

## Material changes

1. `deliverable_original` preserves the ledger sentence verbatim. The revised deliverable reports only an association consistent with tissue composition contributing to the reversal; it no longer promises a stable gated association or lineage-level refusal.
2. The question now concerns only whether the already-measured attenuation imbalance accounts for the parent reversal. This promotes the critique's Rung-0a analysis to the whole candidate.
3. Removed the absolute-HU window, Phase-S recalibration, planted-effect simulations, retention/support floors, restaging, and tissue-gated census.
4. Corrected `design_template` from `counterfactual-synthesis` to `conditional-observational`; no image is synthesized or edited.
5. Specified the primary analysis: join the frozen tables, restrict primary inference to bands 2 and 3, fit `d = band + HU_imbalance + band × HU_imbalance`, and report band-specific slopes and adjusted contrasts with patient-bootstrap intervals. Band 1 and nonlinear fits are exploratory.
6. Corrected the keystone to unique, joinable audit and outcome rows. These were directly inspected, so status is `INSPECTED_TRUE`. Median HU's sensitivity as a composition proxy remains an explicit residual assumption.
7. Acknowledged that these 99 outcomes were opened in the parent study. This is exploratory successor-design evidence, not a fresh confirmatory census; the 49 reserved cases remain untouched.
8. Preserved a bounded decisive negative: persistence of opposite-signed adjusted band contrasts with bootstrap intervals excluding zero decisively shows that median-HU adjustment did not explain the reversal. A nonsignificant slope or imprecise adjusted result is sensitivity-limited. No outcome rejects all tissue composition, CBV/MTT biology, or another cohort.
9. Tightened the positive: it is observational and consistent with contribution, not causal. Severity, ischemic hypodensity, and partial-volume CSF remain alternatives.
10. Updated scores: feasibility rises because inputs are inspected and local; negative-result value falls from 5 to 4 and is bounded to this proxy; novelty confidence falls to 2 because no broad novelty audit exists.

## Claim identity

This is a narrowing. The original rationale was that tissue imbalance might explain idea-023's cross-band reversal; the revision tests that prerequisite directly and removes the unsupported downstream census promise. The parent result, named measurements, cohort, and tissue-confound hypothesis remain unchanged.

```json
{"claim_retention": "narrowed"}
```
