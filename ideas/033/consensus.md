# Debate summary — idea 033

## Agreed

- In round 1, both sides accepted that ISLES'24 provides follow-up-MRI-derived lesion masks, not an acquisition-time tissue-viability reference independent of later infarct outcome.
- In round 1, both sides agreed that a region-specific model response could distinguish a spatially resolved cue from a global scalar, but could not distinguish a map of tissue state at acquisition from a map of later tissue fate.
- In round 1, the proposer accepted the critic's central objection: the proposed interventions cannot identify the original claim that the model reads gray-white attenuation loss as “already injured” tissue or as an “acute-tissue-injury signal.”
- In rounds 1 and 2, both sides agreed that deleting the injury-state interpretation would change the deliverable sentence and therefore the claim's identity. Under the repository rule, the narrower measurement-level studies must be new successors with `parent_ids` pointing to idea 033, not amendments to this card.
- In round 2, both sides agreed on rejection of the original idea, the `IDENTIFIABILITY_FAILURE` kill code, and the condition for a future injury-state candidate: an obtainable acquisition-time viability reference plus a prespecified test separating already-injured from salvageable sign-positive tissue.
- In rounds 1 and 2, both sides treated two narrower questions as possible successors rather than conclusions of this debate: a measurement-level model-use audit and a model-free center-held-out incremental-information test.

## Unresolved

There is no live disagreement about the disposition of idea 033. The following questions remain outside this card and would have to be assessed for separately registered successors:

- **Could an injury-state claim become identifiable in a different study?** The proposer suggested that an independently validated acquisition-time viability reference could do so, and mentioned a verified reperfusion-grade-stratified design as a possible partial alternative. The critic required an obtainable acquisition-time viability reference independent of the follow-up mask and a prespecified state-discriminating test. Evidence that would settle this is a source-verified cohort containing such a reference and a design showing how it separates baseline irreversible injury from salvageable sign-positive tissue. A reperfusion-stratified observational design would still require separate scrutiny for confounding and would constitute a new candidate.
- **Are either of the two narrower successors sufficiently novel and worthwhile to promote?** The proposer records both as candidates; the critic's prior critique considered the model-free incremental-information test conditionally worthwhile and required a targeted primary-source novelty audit. Evidence that would settle this is a separate literature audit of each exact endpoint, followed by a new card evaluated on its own scientific and practical merits.

## Positions that moved

- **Proposer, round 1:** conceded the fatal identifiability objection in response to the critic's argument that follow-up infarct supervision cannot distinguish present tissue injury from a spatially resolved prognostic cue for later fate. This was an earned concession: the proposer explicitly tested and rejected both a semantic defense of “already injured” and a spatial-coupling defense.
- **Critic, round 2:** moved from an open objection to convergence after the proposer accepted the temporal-identifiability gap and the claim-identity consequence. This was not a substantive concession on the critic's position; it recorded that the objection had been accepted.
- **Proposer, round 2:** reaffirmed the round-1 concession in response to the critic's closure. No new concession occurred, and it was not unearned capitulation; the entry merely recorded the agreed kill code, successor boundary, and revisit trigger.

## Amendments made

No amendment was made to idea 033. At round zero, the idea claimed that a final-infarct model uses gray-white differentiation loss as a map of already injured tissue and as an acute-tissue-injury signal. The debate concluded that removing those phrases would create a different deliverable rather than repair this one.

What is lost is the medically stronger interpretation that the model reads a radiologic sign *as current tissue injury*. The surviving successor questions are narrower: whether a model responds to a prespecified regional attenuation-contrast measurement, or whether that measurement adds center-held-out information about follow-up regional infarct involvement beyond supplied perfusion summaries. Neither may inherit an injury-state interpretation from this card.

## Recommendation

**REJECT.** The original claim is not identifiable from ISLES'24 because its follow-up-infarct target cannot separate a map of tissue state at acquisition from a map of later tissue fate. The single most important thing for the human to verify before adopting the decision is the claim-identity boundary: removing “already injured” and “acute-tissue-injury signal” changes the deliverable and therefore requires a new successor rather than revision in place.

## In plain terms

This idea asks whether a stroke model treats fading contrast between gray and white brain tissue as evidence that tissue is already injured. It proposes changing or removing that contrast and observing how the model's predicted final infarct changes.

The debate concluded that this dataset cannot tell whether the model is reading injury that already exists or merely a baseline warning sign of what will infarct later. Both explanations would produce the same response because the reference label comes from later imaging, so the original idea should be rejected; narrower questions about the contrast measurement can be proposed separately.

The human is being asked to confirm that removing the injury interpretation creates a new claim rather than a revision of idea 033.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Register a new injury-state candidate only if an obtainable acquisition-time viability reference independent of the follow-up infarct mask supports a prespecified test separating already-injured from salvageable sign-positive tissue."}
```
