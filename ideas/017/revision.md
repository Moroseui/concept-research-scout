# Revision — Idea 017

## Outcome

The idea is now one Stage 0 question: does a recoverable Sybil-held-out NLST cohort preserve enough stable, independently supported continuous tracheal-index variation to justify a future model-use experiment? The revision reaches no charter rung and contains no present test of whether Sybil uses tracheal deformity.

## Material changes

1. **Removed concept-direction erasure completely.** The confirmatory and exploratory erasure arms, comparator erasures, and all claims based on them were deleted. Linear erasure cannot distinguish removal of tracheal-shape information from collateral removal of sex-, COPD-, emphysema-, or lung-volume information, and a null cannot exclude nonlinear or distributed encoding.

2. **Narrowed the current experiment to four Stage 0 gates.** The entire study is now: native-DICOM versus final-tensor geometry agreement; direct recovery of a Sybil-held-out or suitable external cohort; T0/T1/T2 longitudinal trait stability; and independent joint support beyond sex, LAA-950 emphysema, lung volume, and reconstruction. These gates answer one question—whether a later use experiment is identifiable—not four model-use hypotheses.

3. **Made the inferential boundary explicit.** Passing every gate establishes only that the use question is askable. A favorable score association, high ICC, or successful covariate adjustment is not evidence that Sybil uses X. The card remains at rung 0.

4. **Deferred rung 1 to a valid input-space intervention.** The sole route upward is a future in-distribution tracheal-reshaping edit that changes continuous index, preserves non-tracheal content within frozen equivalence margins, passes matched sham tolerances, and changes risk on an untouched split. This adopts the intervention-validity standard already required for ideas 008, 011, and 014.

5. **Changed X from a categorical deformity to a continuous primary measurement.** Minimum intrathoracic transverse/AP tracheal index is primary. The inconsistent published categorical cutoffs (<0.67 and <=0.5) are descriptive only, avoiding dependence on a likely sparse severe tail.

6. **Replaced respiratory-pair testing with annual-repeat stability.** NLST has T0/T1/T2 scans but no paired inspiratory/expiratory acquisitions. The revised test uses within-subject ICC across annual scans and reports lung volume as an inflation-sensitive comparator. High ICC is consistent with, but does not prove, fixed remodeling; low ICC weakens that premise.

7. **Added an explicit training-contamination gate.** Any model-score analysis is prohibited until actual released split metadata are inspected and linked to obtainable held-out images, or a suitable external cohort is frozen. “Untouched NLST” is no longer assumed from collection membership.

8. **Rewrote the keystone as the load-bearing conjunction.** The real prerequisite is not merely that Sybil resamples images or that NLST is large. It is that a recoverable held-out cohort contains continuous index variation that survives final preprocessing and remains adequately supported outside its dominant correlates. Status remains `NOT_INSPECTED`, so feasibility and novelty confidence remain capped at 3.

9. **Corrected the prior-failure comparison.** The principal precedent is now idea 009: an attractive mechanical quantity that may be inseparable from co-varying population factors. The joint-support gate is the explicit test of whether idea 017 dies the same way. Annotation-provenance failures do not apply because X and all Stage 0 endpoints are automatic.

10. **Named the standing alternatives and their limits.** Reconstruction, positioning, respiratory state, body habitus, screening prevalence, referral pathway, site, scanner/vendor, and label leakage are addressed individually. The card states that Stage 0 cannot eliminate residual biological or acquisition confounding from an observational score association.

11. **Preserved meaningful negative outcomes without overstating nulls.** Failure of the frozen native-to-tensor agreement margin decisively kills this measurement route. Failure of the frozen independent-support threshold decisively shows that the obtainable cohort cannot identify the proposed contrast. Low ICC weakens the fixed-remodeling premise. In contrast, a null score-index association is sensitivity-limited and says nothing decisive about use; split-linkage failure is a data-access stop.

12. **Corrected scoring and priority.** Mode C identifiability falls from 4 to 2 because the present stage cannot identify use. Negative-result value falls from 5 to 3 because only specified feasibility failures are decisive. The Mode C priority is recalculated from 4.60 to 4.10: `0.30*5 + 0.25*2 + 0.20*5 + 0.15*4 + 0.10*5`.

13. **Removed unsupported readiness claims.** Data readiness is reduced from 4 to 3 because public NLST availability does not prove held-out linkage, repeat usability, covariate availability, or independent support. No novelty claim is made; the bounded-search status remains `NO_DUPLICATE_FOUND_LIMITED_SEARCH`.

14. **Added the original deliverable explicitly.** `deliverable_original` records the original physician-readable sentence. The revised `deliverable_sentence` retains it verbatim as an eventual target while labeling it untestable at Stage 0.

## Claim retention

The anatomical X, model, and eventual physician-readable use claim are unchanged. The current contribution is substantially narrowed from a claimed rung-1 experiment to feasibility gates, but it does not substitute a new deliverable sentence. Under the claim-identity rule this is revision in place, not supersession.

```json
{"claim_retention": "narrowed"}
```
