# Debate summary — idea 045

## Agreed

- The attenuation-selected population is a legitimate scoped estimand: the question concerns association within “viable-attenuation” tissue, not recovery of idea 023’s unconditional association (proposer round 1; critic round 2 accepted that the identity check passes).
- Admission NCCT attenuation is not a neutral filter. Because hypodensity relates to tissue injury and final infarction, excluding voxels by HU can preferentially remove outcome-bearing signal (critic round 1; proposer round 1 conceded the null-interpretation consequence).
- Voxel support, retained-event fraction, and post-gate infarct prevalence alone cannot prove that the Q1-versus-Q4 contrast remains detectable (critic rounds 1–2; proposer rounds 1–2 amended in response).
- Any sensitivity calibration must preserve patient clustering and the real covariate geometry, plant both signs of a fixed contrast upstream of selection, apply the frozen HU gate unchanged, and avoid using observed band directions to tune the simulation (critic round 2; proposer round 2 accepted and specified these conditions).
- The proposed round-2 generator is inadequate for the decisive-negative claim because it makes synthetic outcome independent of HU within CBV quartile. It therefore tests sample-size attrition, not selective removal of an HU-localized hemodynamic association (critic round 3; proposer round 3 conceded).
- Without an external, outcome-independent bound on HU-by-outcome effect modification, a post-gate null is sensitivity-limited and cannot terminate the lineage. A positive directional and precision-bounded association within the gated population remains interpretable as an association and could motivate a separately approved model-use study (round 3).
- The cheap Rung-0a analysis of the existing attenuation audit remains useful for testing whether tissue imbalance plausibly accounts for the parent’s band-2/band-3 reversal, although it is exploratory successor-design evidence because it joins already-open outcome-derived values (critique and proposer round 3).

## Unresolved

### Does weakening the negative claim change the candidate’s identity?

- **Question:** Can idea 045 be revised in place after replacing its lineage-terminal, “decisively refusing” negative with a sensitivity-limited, non-terminal null?
- **Proposer’s position:** The scientific question and positive estimand are unchanged, but the deliverable sentence loses a material promise; the proposer explicitly routes the identity determination to human governance.
- **Critic’s position:** The critic did not take a position on the governance boundary. The substantive criticism requires weakening the negative claim.
- **What would settle it:** A human application of the 2026-08-10 claim-identity rule to the old and revised deliverable sentences. This is a governance judgment, not a missing empirical fact.

### Can a future calibration restore a decisive conditional negative?

- **Question:** Is there a defensible quantitative bound on how much of the pre-gate Q1-versus-Q4 association may be concentrated in HU strata excluded by the gate?
- **Proposer’s position:** No such bound is currently available; an unrestricted worst case permits all signal to lie in excluded voxels, so every current post-gate null must remain sensitivity-limited.
- **Critic’s position:** A decisive negative would require an externally bounded effect-modification family and successful recovery of both signs in every band under that family.
- **What would settle it:** Primary external evidence or an independent, non-census-label measurement that quantitatively bounds HU-by-outcome effect modification in the deficit region. Without that evidence, the decisive-negative interpretation cannot be recovered.

### Should the reduced study still run?

- **Question:** Is a study with an interpretable positive but only a sensitivity-limited negative worth advancing beyond the existing Rung-0a CSV analysis?
- **Proposer’s position:** Yes. Rung 0a is cheap and decision-grade; a positive gated census remains useful, while a null must be reported with its limitation.
- **Critic’s position:** The critic established that the census cannot support the advertised decisive negative, but did not argue that the positive arm or Rung 0a is invalid.
- **What would settle it:** First run the prespecified Rung-0a attribution analysis. Its result can determine whether tissue imbalance plausibly explains the reversal and whether the cost of a gated census is justified. The ultimate willingness to fund a one-sided-informativeness study is a human value judgment.

## Positions that moved

- **Proposer, round 1:** Conceded that adequate voxel support alone cannot make a post-gate null decisive after the critic explained that the HU gate may remove outcome-bearing voxels. The proposer added outcome-retention and planted-effect gates plus a classification fork. This concession was earned.
- **Proposer, round 2:** Conceded that “recover planted effects” was underspecified after the critic showed that a generic or post-gate injection would not test the target estimand. The proposer specified a ±0.15 parent-anchored contrast, both signs, preserved patient/covariate structure, synthetic-label separation, and frozen ordering. This concession was earned.
- **Proposer, round 3:** Conceded the decisive-negative claim after the critic showed that the proposed generator assumed HU ignorability within CBV quartile and therefore assumed away the dangerous selection mechanism. The proposer withdrew lineage terminality and accepted a sensitivity-limited null absent an external effect-modification bound. This concession was earned.
- No unearned capitulation occurred.

## Amendments made

At round zero, the idea claimed that a tissue-gated census could either establish a directionally stable association or decisively refuse the Stage-0 prerequisite, with a negative terminating the lineage.

The debate first added outcome-retention checks, planted-effect recovery, a frozen HU window, and a rule that failed sensitivity gates prevent a decisive interpretation. It then made the proposed calibration more explicit: the minimum contrast was anchored to the parent’s 0.15 bound, both signs had to be recovered in every band, patient clustering and covariate geometry were preserved, and real labels were withheld from synthetic calibration.

The final concession supersedes the strongest part of those amendments. Because the generator cannot protect against unknown HU-by-outcome effect modification, the current idea may claim an interpretable positive association within the attenuation-selected population, but a null is sensitivity-limited, non-terminal, and cannot “decisively refuse” the parent formulation. Lost from round zero are the decisive-negative classification, negative-result-value claim of 5, and promised terminal closure. The card also still needs the critique’s earlier repairs: make Rung 0a an imbalance-versus-d attribution analysis with a frozen decision rule, acknowledge reuse of the opened census split, relabel the design as conditional-observational, and scope any positive sentence to equal-patient-weight means.

## Recommendation

**REVISE.** The substantive question retains a viable positive arm and a cheap, useful Rung-0a analysis, but the current card still asserts a decisive, lineage-terminal negative that both sides ultimately rejected. The single most important thing for the human to inspect is whether removing “decisively refusing” and making every null sensitivity-limited preserves the candidate’s identity under the claim-identity rule; if it does, revise the card and scores in place, and if it does not, supersede it with a newly registered successor.

## In plain terms

This idea asks whether a blood-flow pattern is related to later stroke damage after comparing only brain tissue with similar appearance on the admission CT. It first proposes a cheap check of existing data to see whether tissue differences plausibly caused the earlier study’s conflicting results.

The debate concluded that a positive result could still be meaningful, but a negative result would not settle the question: the CT-based filter might remove the very tissue carrying the association. No current external evidence bounds that problem well enough to make a negative decisive, so the written claim must be weakened before the study advances.

The human is being asked whether that weaker negative changes the identity of the idea or can be handled as a revision of the existing card.

```json
{"verdict": "REVISE", "unblock": "Human resolves the claim-identity boundary, then the card is rewritten to preserve only the positive association claim and classify every post-gate null as sensitivity-limited unless an external HU-by-outcome effect-modification bound is obtained."}
```
