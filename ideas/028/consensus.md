# Debate summary — idea 028

## Agreed

- The proposed sinus-intensity intervention can establish, at most, causal sensitivity of a particular model to the edited dural-sinus region; it cannot establish that the model interprets sinus HU as hematocrit or oxygen-carrying capacity. The proposer accepted the critic's objection in round 1, and the critic confirmed the resulting agreement in round 2.
- The original card is internally split between a rung-1 limit (“use of sinus attenuation”) and a stronger question and deliverable about proxy semantics. Both sides agreed by round 2 that narrowing the deliverable to intensity sensitivity would change the claim's identity and therefore could not be an amendment to idea 028.
- The released winning pipeline is not a usable model asset for this intervention: the cited final input set omits NCCT, the official inference implementation uses perfusion-map channels, and the cited preprocessing brain-masks the sinus region. This was raised by the critic and accepted by the proposer in round 1.
- Training a new NCCT-inclusive model could make a regional-intensity sensitivity experiment executable, but would not close the semantic gap. Both sides accepted this in round 1.
- The bare sinus-intensity shortcut audit should not be retained as a successor because the card itself says the study is not worth doing after the hematology link is dropped. Both sides had accepted this by round 2.
- A physiologically direct study would require a treatment-characterized cohort with admission hemoglobin, oxygen saturation, perfusion, reperfusion, time, and final infarct, plus an appropriate frozen model and mediation or substitution analysis. Both sides agreed that this would be a separate candidate, and that the currently verified ISLES'24 release does not supply the required bridge.
- The keystone finding remains reusable: the release provides raw, defaced-only, non-skull-stripped NCCT for 149 cases, with sinus-region anatomy expected to survive. The debate rejected the inference, not the availability of NCCT.

## Unresolved

No substantive disagreement remains between the proposer and critic.

One factual reopening condition remains rather than a live disagreement: whether a cohort concretely linked to ISLES'24 can be obtained with a frozen NCCT-inclusive final-infarct model and temporally aligned hemoglobin, oxygen saturation, acquisition/site, perfusion, reperfusion, and time variables. The proposer and critic both say that such an asset, followed by a preregistered mediation/substitution experiment showing that laboratory-implied sinus HU explains model response while matched nonhematologic edits do not, could justify reconsideration. No such cohort or result was presented in the debate.

## Positions that moved

- **Proposer, round 1:** conceded in response to the critic's substantive argument that the intervention identifies regional-intensity sensitivity rather than oxygen-proxy semantics, that the released winner cannot see the proposed signal, and that narrowing the claim would violate claim identity. This was an earned concession: it directly engaged the objection using the card's rung limit, kill condition, keystone findings, and verified model-asset facts.
- **Critic, round 2:** conceded the debate after the proposer accepted the decisive objection and its consequences. This was agreement on the resulting disposition, not a retreat from the critic's scientific position.
- **Proposer, round 2:** repeated the round-1 concession after the critic had accepted it. No new argument was offered or needed; this procedural closing is not an UNEARNED substantive concession because the position had already moved for stated reasons in round 1.

The debate substantively converged in round 1 after a real objection was raised and answered; round 2 recorded mutual closure.

## Amendments made

No amendment was made. At round zero, idea 028 claimed that a final-infarct model uses venous-blood NCCT attenuation as a proxy for oxygen-carrying capacity. The only claim supported by the proposed intervention would be sensitivity to edited dural-sinus intensity. Both sides agreed that substituting that weaker claim would create a different candidate, and they did not recommend registering it.

What is lost is the candidate's defining physiological interpretation: neither hematocrit nor oxygen-carrying-capacity semantics can be inferred from a monotone model response to sinus-HU edits. The nearby laboratory-cohort question retains that motivation but is a separate proposal and may fall outside the ISLES'24 charter because ISLES'24 would not currently be load-bearing.

## Recommendation

**REJECT.** The design cannot distinguish use of dural-sinus intensity from use of that intensity *as an oxygen-carrying-capacity proxy*, and the narrower identifiable claim changes the idea's identity and fails its own value condition.

The single most important thing for the human to inspect is whether the asserted reopening asset actually exists: an obtainable cohort concretely linked to ISLES'24 that combines a frozen NCCT-inclusive final-infarct model with temporally aligned hematology, oxygen saturation, treatment/reperfusion, perfusion, time, and acquisition/site data. Without that bridge, there is no factual basis to preserve idea 028.

## In plain terms

This idea asks whether a stroke model reads the brightness of blood in large head veins as a rough measure of how much oxygen the blood can carry. It proposes changing only that brightness and observing whether the model's predicted final injury changes.

The debate concluded that such a response would show only that the model reacts to the edited brightness, not that it treats brightness as an oxygen measure. The available winning model also does not use the relevant CT image region, and weakening the claim would turn this into a different, explicitly low-value study. The human is being asked to judge whether a specifically linked cohort with the missing laboratory, treatment, imaging, and model assets exists strongly enough to justify reopening the idea.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Obtain an untouched treatment-characterized cohort concretely linked to ISLES'24, a frozen NCCT-inclusive final-infarct model, and temporally aligned hemoglobin, oxygen saturation, acquisition/site, perfusion, reperfusion, and time data sufficient for a preregistered mediation/substitution test."}
```
