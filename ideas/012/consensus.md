# Debate summary — idea 012

## Agreed

- The original partial-regression analysis cannot establish that Sybil uses coronary artery calcium. Adjustment for pack-years, emphysema, and BV5 leaves many correlated ageing, smoking, vascular, habitus, and acquisition explanations; it identifies conditional association, not feature use (critic round 1; proposer accepted in round 1).
- The paired-kernel arm cannot identify CAC-specific use because reconstruction changes calcium blooming, emphysema measurements, noise, edges, and texture together. At most it establishes sensitivity to a generic reconstruction- or density-dependent signal (critic round 1; proposer accepted in round 1).
- A CAC-specific rung-3 claim would require a controlled within-scan intervention on AI-CAC lesion masks, realistic counterfactual generation, matched coronary-sham and noncoronary-calcium controls, and fidelity/positive-control gates. Simple voxel deletion would repeat idea 006's out-of-distribution problem (both sides, round 1).
- The released Sybil materials do not permit outsiders to reconstruct the published cohort with no visible nodule at the future cancer site. The paper verifies that the residual AUC was measured, but the load-bearing scan-level MD.ai-derived membership is unreleased (proposer accepted in round 1 and reaffirmed in round 2).
- The card therefore made a wrong-keystone error: it marked the existence of the published residual analysis as sufficient when the required fact was that the exact cohort could be reconstructed and joined to an obtainable frozen Sybil evaluation split (both sides by round 2).
- A public screen-level NLST nodule code is not an adequate substitute. It is neither spatially specific to the later cancer site nor produced by the same informed readers, and it cannot be validated against the unreleased membership (proposer round 2, consistent with the critic's round-2 requirement).
- Testing CAC removal on an ordinary screening subset is a different estimand from explaining Sybil's published future-cancer-site-nodule-excluded residual. Effects may differ across scans with visible lesions, controls, and the residual cohort, so neither a positive nor a null in the general subset answers the original Mode A question (critic round 2; proposer conceded in round 2).
- Idea 012 should remain paused until the original cohort is reproducibly obtainable. The general Sybil/CAC inpainting experiment may be retained as a separate Mode B candidate, not as an amendment to this idea (both sides, round 2).
- Because Sybil clips values above approximately +150 HU, the mechanistically faithful X is coronary-calcium presence and extent after Sybil preprocessing, not Agatston density weighting as perceived by Sybil (proposer round 1; not disputed).

## Unresolved

No substantive disagreement remained after the proposer's round-2 concession. The factual unblock condition is clear: obtain either (a) the scan-level future-cancer-site-nodule-exclusion membership used by Mikhael et al., joinable to a frozen obtainable Sybil evaluation split, or (b) a public, prospectively specified machine-computable rule validated against that membership with sufficient agreement to preserve the cohort estimand. Even after that evidence appears, the CAC-use claim would still require the fidelity-gated intervention and matched controls accepted in round 1.

## Positions that moved

- **Proposer, round 1:** Conceded that partial regression cannot turn CAC's conditional association into evidence of CAC-specific use, and that paired reconstruction changes establish only generic density/reconstruction sensitivity. This was earned by the critic's concrete omitted-correlate and joint-perturbation arguments.
- **Proposer, round 1:** Downgraded the claimed keystone after accepting the repository evidence that the MD.ai-derived cohort membership is unreleased. This was earned by direct inspection evidence summarized in the critique and invoked in the debate.
- **Proposer, round 1:** Initially treated the general screening-LDCT intervention as an amendment that preserved the mechanism clause while dropping the cohort clause. The proposer explicitly acknowledged that this lost the Mode A hook.
- **Critic, round 2:** Tightened the earlier permissive view of whether the general-subset intervention could remain Idea 012, clarifying that retaining or reproducibly reconstructing the residual cohort was a condition of preserving the question. This was a clarification of the identity criterion, not a concession on the scientific objection.
- **Proposer, round 2:** Conceded that the round-1 amendment failed the identity check and accepted PAUSE for Idea 012, with the general intervention moved to a separate Mode B candidate. This was earned by the critic's effect-heterogeneity and estimand argument and by the proposer's subsequent check showing that public NLST abnormality codes cannot reproduce or validate the spatial exclusion.
- No concession was unearned.

## Amendments made

At round zero, Idea 012 claimed that partial association of Sybil score with automated Agatston-equivalent CAC—after adjustment for pack-years, emphysema, and BV5, supplemented by a paired-kernel arm—could explain Sybil's published residual performance in scans without a visible nodule at the future cancer site.

In round 1, the proposer temporarily replaced that design with realistic within-scan inpainting of AI-CAC-segmented coronary lesions, compared against size- and attenuation-matched aortic-calcium edits and calcium-free coronary-territory sham edits. The proposal added HU-space and post-Sybil-transform fidelity checks, AI-CAC suppression as a positive control, and restated X as calcium presence and extent surviving Sybil's preprocessing. It dropped partial regression, mediation, the cancer endpoint, and the exact residual cohort; the 0.81 residual became motivation only. Negative-result value became conditional on intervention fidelity and a prespecified detectable-effect threshold.

In round 2, that amendment was withdrawn from Idea 012 because it changed the estimand. The controlled-inpainting design survives only as a proposed separate Mode B candidate. Idea 012 retains its original Mode A question but makes no current feature-use claim and is paused. Lost from the executable idea are the published-residual venue, its quantified 0.81 anchor as a directly testable cohort result, and the original high-regret claim that this residual can presently be decoded from public assets.

## Recommendation

**PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.
