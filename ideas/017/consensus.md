# Debate summary — idea 017

## Agreed

- The original linear concept-direction erasure experiment cannot identify whether Sybil uses tracheal deformity. A positive effect could reflect removal of correlated sex-, COPD-, emphysema-, or lung-volume information, while a null could reflect nonlinear or distributed encoding. The proposer accepted this objection in Round 1, and the critic confirmed agreement in Round 2.
- The erasure arm must be removed entirely, including from exploratory criteria. Separate erasures or covariate adjustment do not repair the causal-use inference. Agreed in proposer Round 1 and critic Round 2.
- The current study reaches no charter rung. Its four analyses are Stage 0 go/no-go feasibility gates only; even favorable results do not establish that Sybil uses tracheal deformity. Agreed in proposer Round 1 and critic Round 2.
- The four Stage 0 gates are: native-DICOM versus final-tensor geometry preservation; recovery of a Sybil-held-out or external evaluation split; within-subject stability of continuous tracheal index across NLST T0/T1/T2 scans; and adequate joint support beyond sex, LAA-950 emphysema, lung volume, and reconstruction kernel. Agreed in proposer Round 1 and critic Round 2.
- Continuous minimum tracheal index is the primary measurement. Categorical saber-sheath thresholds are descriptive only because published thresholds differ and severe categorical cases may be too sparse. Agreed in proposer Round 1 and critic Round 2.
- Annual NLST repeats are a more defensible stability test than unavailable inspiratory/expiratory NLST pairs or an out-of-distribution external 4DCT cohort. High stability is consistent with fixed remodeling but is not evidence of model use; low stability is evidence against the proposed fixed-remodeling mechanism. Agreed in proposer Round 1 and critic Round 2.
- All score associations must use a recoverable Sybil-held-out or external set; the released split metadata must be inspected rather than assuming that “untouched” NLST cases can be identified. Agreed in proposer Round 1 and critic Round 2.
- The relevant prior failure is idea 009: a mechanically meaningful quantity may be inseparable from co-varying population factors. The joint-support audit is the explicit test of whether idea 017 dies the same way. Agreed in proposer Round 1 and critic Round 2.
- Rung 1 remains deferred unless an input-space tracheal-reshaping intervention is shown to be in-distribution, preserves non-tracheal content within prespecified equivalence margins, passes a sham-edit tolerance, and changes risk on an untouched split. Agreed in proposer Round 1 and critic Round 2.
- The original identifiability and negative-result claims were overstated. The withdrawn design's identifiability is 2 rather than 4, and a null score–index association is sensitivity-limited rather than decisive. Agreed in proposer Round 1 and made auditable in proposer Round 2.

## Unresolved

There was no substantive disagreement left after the Round 1 amendment. The following are empirical uncertainties shared by both sides, not disputed positions:

- **Does Sybil preprocessing preserve continuous tracheal index accurately enough?** The proposer and critic both treat native-to-final-tensor agreement as a mandatory gate. Paired measurements on actual NLST DICOMs and Sybil tensors, assessed against a prespecified agreement margin, would settle it.
- **Can Sybil's held-out NLST cases be recovered, or can a suitable external cohort be used?** Both sides require evaluation outside the training set. Direct inspection of released split metadata and successful linkage to obtainable images would settle it.
- **Is continuous tracheal index a stable longitudinal trait in NLST?** Both sides accept T0/T1/T2 within-subject ICC as the test and lung volume as an inflation-sensitive comparator. A prespecified ICC analysis on repeat scans would settle the feasibility claim; it would not establish model use.
- **Is there adequate tracheal-index support independent of sex, emphysema, lung volume, and reconstruction?** Both sides regard this as the idea-009-style lives-or-dies gate. A prespecified joint-distribution and partial-correlation audit, including a minimum effective low-index sample requirement, would settle whether the use question is identifiable in the obtainable cohort.
- **Can a valid tracheal-reshaping intervention be constructed?** The proposer accepts and the critic requires an in-distribution edit with sham tolerance and equivalence margins for all non-tracheal content. Validation on held-out real scans, including discriminator or distributional checks and matched sham edits, would determine whether a rung-1 experiment is available. Until then, the model-use question remains deferred.

## Positions that moved

- **Proposer, Round 1:** conceded the critic's central objection that concept-direction erasure cannot identify selective use. The concession directly answered the critic's evidence about collateral removal of correlated features, nonlinear encodings surviving erasure, and the unusually strong sex/COPD/emphysema collinearity of saber-sheath deformity. This was an earned concession.
- **Proposer, Round 1:** withdrew the claim that the current cycle could reach rung 1 and replaced it with a Stage 0-only feasibility study. This followed from the same identifiability objection and was an earned concession.
- **Proposer, Round 1:** accepted continuous index as primary, annual-repeat stability in place of respiratory pairs, held-out-split inspection, comparison with idea 009, and lower scores. These changes responded to specific prevalence, distribution-shift, leakage, and identifiability evidence in the critique and Round 1 objection; none was unearned.
- **Critic, Round 2:** conceded that the amendment resolves the fatal objection because the proposer deleted erasure and cleanly separated feasibility estimands from any model-use claim. This was earned by the substantive Round 1 amendment.
- **Proposer, Round 2:** conceded that nothing remained in dispute and translated the agreement into auditable card requirements. No new scientific concession occurred, and this was not unearned capitulation.

## Amendments made

At round zero, the idea claimed that selective erasure of a validation-learned tracheal-index direction, compared with emphysema, sex, lung-volume, and random-direction erasures, could establish rung-1 model use in roughly one week. It also treated paired respiratory scans as a stability gate, used a categorical threshold prominently, classified a null erasure as decisive, and scored identifiability 4 and negative-result value 5.

The amended idea makes no present model-use claim and reaches no rung. It is a Stage 0 feasibility study comprising only geometry preservation, held-out-split integrity, longitudinal trait stability, and joint-support audits. Continuous tracheal index is primary; categorical thresholds are descriptive. No erasure analysis remains. A future rung-1 study is conditional on all four gates passing and on validation of an in-distribution input-space tracheal edit with sham and preservation controls.

What is lost is substantial: the one-week path to a rung-1 result, the decisive interpretation of a null model response, the high identifiability score, and the original negative-result-value score. What remains is a cheaper feasibility result that can either justify attempting the harder intervention or decisively stop the project if preprocessing destroys X or the obtainable cohort cannot separate X from its dominant correlates.

## Recommendation

**REVISE.** Rewrite `idea_card.json` to implement the converged Stage 0-only design before any feasibility memo or probe contract. The single most important thing for the human to inspect is whether the joint-support gate can be given a prespecified, adequately powered minimum-support criterion: if continuous tracheal index cannot be separated from sex, emphysema, lung volume, and reconstruction in a recoverable held-out cohort, idea 017 dies like idea 009 regardless of the attractiveness of its mechanism.

```json
{"verdict":"REVISE","unblock":"Rewrite the idea card as a four-gate Stage 0-only study with no erasure or use claim, then prespecify and inspect adequate independent tracheal-index support in a recoverable Sybil-held-out or external cohort."}
```
