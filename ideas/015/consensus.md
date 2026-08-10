# Debate summary — idea 015

## Agreed

- The proposed BAC inpainting experiment cannot establish that Mirai uses breast arterial calcification as a systemic vascular-age signal. An independent cardiovascular-age endpoint unavailable to Mirai would be required for that interpretation (round 1).
- The defensible current question is whether frozen Mirai's five-year risk score responds specifically to breast arterial calcification, rather than merely to calcification in general (round 1).
- The primary test should compare BAC inpainting with two controls: matched benign parenchymal-calcification deletion and equal-area non-calcific linear-structure deletion. Both sides accept this as a credible test of arterial-location or morphology sensitivity versus generic calcification sensitivity (rounds 1–2).
- Even a positive result from that experiment would not distinguish vascular ageing from lesion mimicry or another BAC-correlated image feature (rounds 1–2).
- The current claim must not say that BAC causes inflated breast-cancer risk estimates. A label-free score intervention establishes score sensitivity, not outcome calibration; calibration or equity conclusions require linked cancer outcomes and a calibration analysis (round 2).
- The current preregistered endpoint should therefore be limited to BAC-specific score response, with both vascular-age encoding and miscalibration treated as unclaimed downstream questions (round 2).
- The narrower experiment remains worthwhile in light of the closest prior work, DOI 10.1148/ryai.240417, which establishes Mirai reliance on calcification features generally but does not resolve arterial versus lesion calcification (rounds 1–2).

## Unresolved

### Should the narrowed BAC-response study remain Idea 015 or be registered separately?

- **Proposer's position:** It is a revision in place. Mirai, the named X (breast arterial calcification), assets, keystone, confounds, and intervention remain the same; only an unearned rung-3 interpretation has been removed. The charter expressly permits a candidate to stop at rung 2 while naming what would be needed for rung 3, and Idea 007 supplies a precedent for demotion without a fork.
- **Critic's position:** It is a replacement. The original distinguishing question was whether Mirai uses BAC *as vascular age*; the proposer conceded that the revised experiment cannot answer that question. Shared assets and motivation do not preserve candidate identity after removal of the defining causal interpretation.
- **What evidence would settle it:** No empirical result would settle this registration dispute. It is a governance question about whether candidate identity follows the model and named X or the original mechanistic interpretation. The human must apply a consistent portfolio rule, with the charter's rung-demotion language and the Idea 007 precedent weighed against the rule that abandoning a defining question requires a new candidate.

### What would restore the original vascular-age claim?

- **Proposer's position:** The claim is an aspirational rung-3 extension and cannot be tested with any currently confirmed cohort.
- **Critic's position:** It can remain Idea 015 only if a Mirai-compatible cohort supplies an independently measured cardiovascular-age endpoint and supports analysis beyond chronological age and density.
- **What evidence would settle it:** Confirmation of an obtainable Mirai-compatible mammography cohort linked to an independent endpoint such as CAC, validated arterial age, or cardiovascular outcomes, followed by evidence that the BAC-dependent component of Mirai's score tracks that endpoint within narrow age and density strata while an intervention separates arterial BAC from matched parenchymal calcification.

## Positions that moved

- **Proposer, round 1:** Conceded the critic's argument that BAC-pixel sensitivity cannot identify vascular-age encoding. In response, the proposer removed “as a vascular clock” from the title, narrowed the question and deliverable to BAC-specific score response, lowered the target from rung 3 to rung 2, and made vascular age an explicitly unclaimed extension. This concession was earned by the critic's identifiability argument and the same-model evidence of generic calcification reliance.
- **Proposer, round 1:** Strengthened the intervention from a representation-direction erasure design to image-space BAC inpainting with matched benign parenchymal-calcification and non-calcific linear-structure controls, in response to the critic's generic-calcification and lesion-mimicry alternatives.
- **Proposer, round 2:** Conceded that “inflated risk estimates” is a miscalibration claim unsupported by a label-free intervention and struck it from the motivation. This concession was earned by the critic's distinction between score sensitivity and outcome calibration.
- **Critic, rounds 1–2:** Accepted that the narrower BAC-specific response experiment is credible and worthwhile, but did not move on the requirement to register it as a separate candidate.
- No concession was unearned.

## Amendments made

At round zero, Idea 015 claimed that Mirai uses BAC as a vascular-age signal independently of chronological age and breast density, targeted rung 3, and proposed validation-learned embedding-direction erasure as its confirmatory test.

The amended study claims only that Mirai's risk output responds specifically to breast arterial calcification—the linear tram-track calcium in mammary arteries—and not merely to calcification in general. It targets rung 2 and uses paired image-space BAC inpainting as the primary readout, compared with matched benign parenchymal-calcification deletion and equal-area non-calcific linear-structure deletion. Representation erasure is no longer the primary identifying instrument.

The amended study expressly does not claim vascular-age encoding, inflated risk, miscalibration, or an equity effect. Vascular age would require an independent cardiovascular endpoint; calibration would require cancer outcomes and calibration analysis.

What was lost is the original high-interest mechanistic headline: “a breast-cancer model found a vascular clock.” The remaining claim is narrower but still physician-legible and tests a precise delta left open by prior work on Mirai's general calcification reliance.

The repository's current `idea_card.json` still contains the superseded round-zero title, question, rung, deliverable, embedding-erasure primary experiment, calibration implication, and scores; it therefore requires revision before advancement regardless of the registration decision.

## Recommendation

**REVISE.** The scientific design has converged, but the card has not been updated and the candidate-registration dispute remains irreducible. Before deciding, the human should make one explicit portfolio-governance choice: whether removal of the original vascular-age interpretation is an allowed rung demotion within Idea 015 or requires the agreed BAC-response experiment to be registered as a new candidate. Either choice should preserve the same narrowed experiment and prohibited conclusions; advancement should then remain conditional on Stage 0 confirming an obtainable Mirai-compatible cohort and spatial registration between the BAC mask and Mirai's exact input tensor.

```json
{"verdict":"REVISE","unblock":"Choose revision-in-place versus re-registration, then update the card to the agreed BAC-specific claim and verify the Mirai-input/BAC-mask join on an obtainable compatible cohort."}
```
