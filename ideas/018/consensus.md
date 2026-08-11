# Debate summary — idea 018

## Agreed

- The original study is not executable with currently obtainable assets (Round 1 proposer concession; Round 2 closure). The publication-linked GRASP repository has training code but no released checkpoint, pretrained weights, inference entry point, or released training cohort, while the paper makes its data available only by request.
- The proposed longitudinal arm also lacks a suitable public cohort (Round 1 proposer concession). LUMIERE is skull-stripped and removes the temporalis; the UPenn-GBM follow-up subset consists of second-resection cases selected for progressive radiographic change rather than the required tumor-stable pairs.
- These are two independent failures of the conjunctive keystone: neither an obtainable runnable GRASP model nor an obtainable survival-linked serial cohort retaining temporalis with enough tumor-stable pairs was established (Round 1), and the relevant GRASP-route conjuncts should be treated as `INSPECTED_FALSE` rather than merely unresolved (Round 2).
- Replacing GRASP with a newly trained UPenn-GBM model and replacing the longitudinal arm with cross-patient substitution changes the audited object and estimand (Round 1). Under the claim-identity rule, this is a separate successor with `parent_ids: ["idea-018"]`, not a revision of Idea 018.
- The original frailty interpretation is not identified by a positive temporalis substitution result because age and sex remain plausible meanings of the same signal (Round 1). Any successor's deliverable must be limited to “the model is using temporalis muscle bulk”; systemic frailty may appear only as a hypothesis in discussion.
- The successor should retain four constraints (Round 2): an age-adjusted arm; a preregistered gate requiring the self-trained model to beat an age+sex-only baseline on a frozen split; Stage 0 confirmation that CaPTk defacing spares temporalis at standardized measurement levels; and an independent novelty audit, including a search for temporal-region saliency or occlusion results in GRASP and its citing literature.
- The public automated temporalis measurement method and the medical motivation survive, but they do not rescue the original GRASP-focused study (Rounds 1–2).

## Unresolved

There are no unresolved disagreements between proposer and critic. Both agree that reopening Idea 018 would require two concrete assets: an openly runnable frozen GRASP checkpoint with exact preprocessing, and an obtainable survival-linked serial cohort retaining bilateral temporalis with a prespecified adequate number of same-patient, tumor-stable pairs. Whether those assets may become available is an external factual question, not a remaining dispute; direct inspection of released artifacts and cohort records would settle it.

The feasibility, identifiability, and novelty of the proposed UPenn-GBM successor were not adjudicated in this debate. They must be evaluated in a new scouting cycle, beginning with direct inspection of temporalis preservation after defacing and a dedicated prior-work audit.

## Positions that moved

- The proposer conceded in Round 1 that both load-bearing assets fail direct inspection, responding to the critic's repository, paper, and public-cohort evidence. This was an earned concession based on specific evidence.
- The proposer conceded in Round 1 that the feasible UPenn-GBM repair changes claim identity and must become a separate successor, responding to the critic's application of the idea-015 governance precedent. This was earned.
- The proposer also corrected the original `dies_like_prior` analysis in Round 1: the card had noticed use-versus-association risk but missed the idea-014 family of missing model-asset failure. This correction followed the critic's direct asset inspection and was earned.
- In Round 2, the critic accepted that the Round 1 concession resolved the sole objection and closed the debate. The proposer's Round 2 response merely fixed the disposition and successor constraints; it did not make a new concession. No concession was unearned.

The debate did not converge without objection: the critic raised a specific fatal objection in Round 1, supported it with direct asset and cohort inspection, and the proposer substantively answered and conceded it.

## Amendments made

Idea 018 itself was not amended into a feasible study. At round zero it claimed that a runnable whole-head GRASP survival model could be audited with tumor-stable longitudinal tracking and temporalis-only substitution, supporting the sentence “the glioblastoma survival model is using temporalis muscle thickness as an image marker of systemic frailty.” The debate established that the required model and longitudinal cohort are unavailable and that “systemic frailty” is not identified.

The proposed successor would instead train a new whole-head survival model on UPenn-GBM baseline scans and test whether it uses automatically measured temporalis muscle bulk through cross-patient substitution and shams. Lost in that transition are any claim about GRASP, the within-patient tumor-stable estimand, and the frailty interpretation. Because those losses change claim identity, the successor is not an amendment and inherits no queue position.

## Recommendation

REJECT Idea 018. The single most important thing for the human to check before changing that decision is whether **both** reopening assets now exist: an openly runnable frozen GRASP checkpoint with exact preprocessing and an obtainable survival-linked serial cohort retaining bilateral temporalis with enough prespecified tumor-stable within-patient pairs. The UPenn-GBM proposal should be considered separately through normal scouting with `parent_ids: ["idea-018"]`.

```json
{"verdict": "KILL", "kill_code": "DATA_ACCESS", "unblock": "Provide both an openly runnable frozen GRASP checkpoint with exact preprocessing and an obtainable survival-linked serial cohort retaining bilateral temporalis with an adequate prespecified count of tumor-stable same-patient pairs."}
```
