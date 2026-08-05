# Debate summary — idea 010

## Agreed

- The proposed observational association between CT-CLIP's cardiomegaly score and automatic heart-size measurements cannot establish that the model uses absolute heart volume in millilitres. Volume, diameter, silhouette area, shape, and indexed size are correlated consequences of the same anatomy, so comparative prediction among them does not identify the model's cue (critic rounds 1–2; proposer accepted in round 3; critic confirmed convergence in round 4).
- The intended natural contrast between physical heart volume and heart fraction of the input frame does not exist under the inspected CT-CLIP preprocessing. The loader resamples scans to fixed spacing and then crops or pads them to a fixed physical box, making voxel occupancy proportional to physical volume; residual occupancy differences would reflect truncation, positioning, coverage, or spacing errors rather than a clean apparent-size contrast (proposer round 3; critic accepted in round 4).
- The design contains no intervention, ablation, perturbation, occlusion, or valid independent measurement test and therefore does not reach rung 1. It cannot support the original rung-3 sentence (proposer round 3; critic round 4).
- The claim that absolute-volume reliance causes over-calling in large patients and under-calling in small patients is unsupported. It would require an independent clinical reference, a frozen operating threshold, and a definition of patient size; CT-RATE's report-derived Cardiomegaly label is not an independent reference for clinical error (critic rounds 1–2; proposer conceded in round 3; critic accepted in round 4).
- The card's `keystone_status` should not be `INSPECTED_TRUE`. Repository file presence and class-map entries were inspected, but runnable paired scores, valid same-volume measurements, sufficient conditional variation, and adequate score range were not. The load-bearing prerequisite is therefore uninspected, and feasibility and novelty confidence remain capped at 3 (proposer round 3; critic accepted in round 4).
- A screening analysis asking which automatic measurement best predicts the score could be a go/no-go audit, but it answers a different associational question and must not be presented as evidence that the model uses millilitres (critic rounds 1–2; proposer round 3).
- A whole-body scale perturbation would test sensitivity to global absolute physical scale, not cardiac volume specifically. It is a separate, narrower candidate requiring interpolation, crop-truncation, in-distribution, and size-irrelevant-label controls; it does not rescue Idea 010 (proposer round 3; critic round 4).

## Unresolved

There is no remaining disagreement about the original candidate. Both sides agree that the recorded design and deliverable are unsupported.

Reopening would require new evidence rather than resolution of a current dispute: an independently validated, in-distribution heart-specific intervention or a verified natural same-patient asset that changes three-dimensional cardiac volume while holding thoracic scale, leading silhouette and shape cues, preprocessing artifacts, and noncardiac anatomy fixed. Restoring any over/under-calling claim would additionally require an independent clinical reference and a frozen operating threshold.

The scientific value of the proposed global-scale spin-off was not debated to resolution because both sides classified it as outside Idea 010. It would need a separate idea card and adversarial review.

## Positions that moved

- **Proposer, round 3:** Conceded the critic's rounds 1–2 identifiability objection. This was earned: the critic had shown that observational ranking of correlated measurements cannot identify volume use, and the proposer added direct loader-based evidence showing that the claimed millilitres-versus-frame-fraction contrast collapses under fixed-spacing, fixed-box preprocessing.
- **Proposer, round 3:** Withdrew the body-size-dependent over/under-calling clause in response to the critic's argument that no independent clinical reference or frozen threshold exists. This was earned by the explicit measurement requirements raised in rounds 1–2.
- **Proposer, round 3:** Reclassified the keystone as uninspected and acknowledged the corresponding score caps. This responded to the critique's nearest-checkable-fact objection and the proposer's own review of what had actually been inspected.
- **Critic, round 4:** Conceded to the proposer's more specific loader-based identity argument and accepted that the intended natural contrast is mathematically absent except through artifacts. This was earned by new, directly inspected preprocessing evidence supplied in round 3.
- No concession was unearned. Round 2 contained no movement because no proposer response or new evidence had yet been supplied.

## Amendments made

No amended version of Idea 010 was defended.

At round zero, the idea claimed that CT-CLIP uses absolute heart volume in millilitres rather than heart size relative to the chest, reached rung 3, and consequently over-calls cardiomegaly in large patients and under-calls it in small patients. By convergence, all of those claims were withdrawn. The surviving observational audit can say only which automatic heart-size measurement best predicts the score in this corpus; it cannot say which signal the model uses and is not a rung-1 result.

What was lost is the candidate's mechanistic deliverable, its clinical error claim, its rung-3 status, and its asserted inspected keystone. The proposed global physical-scale perturbation was explicitly separated as a new candidate with a narrower claim.

## Recommendation

**REJECT.** The single most important fact for the human to inspect is the loader-based collapse of the proposed discriminator: after fixed-spacing resampling into a fixed physical box, heart voxel occupancy is proportional to heart volume, so the study has no independent millilitres-versus-frame-fraction contrast. Reconsider only if a credible heart-specific, in-distribution intervention or paired natural experiment is identified.
