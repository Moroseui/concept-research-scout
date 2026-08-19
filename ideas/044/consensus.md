# Debate summary — idea 044

## Agreed

- The proposed NCCT intervention can test whether a frozen final-infarct model uses contralateral chronic-cavity-like appearance in the NCCT channel, but it cannot establish that the model interprets that appearance as reduced brain reserve (rounds 1–2).
- Under this design, brain reserve, age proxy, prior vascular-disease burden, and a bare morphology–label association remain observationally equivalent explanations of a positive edit response (rounds 1–2).
- ISLES'24 contains no independent reserve measurement or intervention capable of separating those explanations (rounds 1–2, reaffirmed in rounds 4–6).
- A defensible narrower study would explicitly claim only NCCT-channel use of contralateral cavity-like appearance. Its positive result could not be described as evidence that the model measures reserve, age, vascular-disease burden, or proven prior infarction; its null could not exclude use of cavity information in other channels (round 2, accepted in rounds 4–6).
- The narrower experiment remains scientifically worth considering. It should retain the frozen-model and numeric-performance pin, an NCCT-sensitivity ablation gate, normal-tissue donor exclusions, a power-derived census over all 149 public cases, and the CSF sham as the cross-channel mismatch control (rounds 2 and 4–6).
- Changing the deliverable from a brain-reserve mechanism claim to a cavity-appearance sensitivity claim changes both the deliverable sentence and the prohibited-conclusions set. Under the written 2026-08-10 claim-identity rule and its idea-015 precedent, that requires superseding idea 044 and sending the narrower study through the normal pipeline as a lineage-linked candidate (rounds 3–6).
- No fatal objection was found to the narrower experiment itself. The failure concerns the registered claim that the experiment was supposed to identify (rounds 4–6).

## Unresolved

### Should the idea-023 disposition create an exception to the written claim-identity rule here?

- **Question:** May the human treat removal of the reserve interpretation as a revision in place, following the case-specific handling of idea 023, despite the standing rule's explicit supersession triggers?
- **Proposer's position:** The proposer initially invoked idea 023 to support revision in place (round 2), then withdrew that argument and accepted supersession as the default because only the human can grant a case-specific exception (round 4).
- **Critic's position:** Idea 023 does not authorize the debate to waive the written rule; idea 044 should be superseded unless the human expressly rules otherwise (rounds 3 and 5).
- **What evidence would settle it:** No empirical evidence can settle this governance question. A human interpretation of the relationship between the 2026-08-10 rule and the later idea-023 disposition is required.

### Can the original brain-reserve claim ever be tested?

- **Question:** Can model use of cavity appearance specifically as a brain-reserve signal be distinguished from age, vascular-disease burden, or morphology–label association?
- **Proposer's position:** Not with ISLES'24 alone; this would require a distinct successor using an independently validated reserve construct (rounds 2, 4, and 6).
- **Critic's position:** The original claim could be retained only if an independent reserve measurement or intervention and a prespecified discriminating contrast were added (rounds 1, 3, and 5).
- **What evidence would settle it:** A cohort or experiment with an independently validated reserve measurement or perturbation, plus a prespecified contrast showing that model response tracks reserve beyond age, prior vascular disease, and cavity morphology.

There is no remaining scientific disagreement between the parties about what the current NCCT edit identifies. The only live issue is the human governance judgment above.

## Positions that moved

- **Proposer, round 2:** Conceded the critic's round-1 identifiability objection and amended every claim surface from “brain reserve” to NCCT-channel use of contralateral chronic-cavity-like appearance. This was earned by the argument that all alternative interpretations remain observationally equivalent and ISLES'24 lacks an independent reserve measure.
- **Proposer, round 4:** Withdrew the round-2 claim that this could be revised in place and conceded supersession. This was earned by the critic's new round-3 governance argument: the amendment changes both fields explicitly named by the 2026-08-10 rule, and the founding idea-015 case is structurally analogous.
- **Critic, round 5:** Closed the objection after the proposer accepted supersession and the lineage-linked successor path. This was earned by the round-4 application of the governing rule and precedent.
- **Proposer, round 6:** Restated the already-supported round-4 concession after the critic accepted it. This added no new concession and is not UNEARNED capitulation; it merely fixed the converged state.

## Amendments made

At round zero, idea 044 claimed that the model uses contralateral chronic infarct cavities **as a marker of reduced brain reserve** when forecasting new infarction. The round-2 amendment instead asks whether a frozen final-infarct model uses contralateral chronic-cavity-like tissue loss in the admission-NCCT channel. Reserve becomes motivation only, and positive results are explicitly barred from establishing reserve, age, vascular-disease burden, or proven prior-infarct etiology.

The amendment also corrects the plain pitch, scopes null conclusions to the NCCT channel, and carries forward five design requirements: a named frozen-model path with a numeric performance gate; a pre-experiment NCCT-sensitivity gate; verified normal donor tissue or fallback inpainting; a power-derived whole-cohort cavity census; and a CSF sham designated as the cross-channel mismatch control.

What is lost is the physician-legible reserve mechanism, some claimed medical relevance and interest, and—under the standing governance rule—the current candidate's shortlist status and queue position. Because the amended claim has a different identity, these amendments define a proposed successor rather than an adopted revision of idea 044.

## Recommendation

**REJECT** idea 044 as superseded because its registered brain-reserve claim is not identifiable with the proposed intervention. The single most important thing for the human to inspect is whether the case-specific handling of idea 023 should override the explicit 2026-08-10 claim-identity rule here; absent that override, the narrower NCCT-channel cavity-appearance study must re-enter normally with `parent_ids: ["isles24-scout-005-c02"]` and fresh ranking.

## In plain terms

This idea asks whether a stroke-prediction model sees an old-looking cavity on the opposite side of the brain and treats it as evidence of reduced brain reserve. The proposed image edit can show whether the cavity's appearance in the plain CT changes the prediction, but it cannot reveal whether the model understands that appearance as reserve rather than age, vascular disease, or a learned visual correlation. Both sides therefore agreed that the original reserve claim should be superseded, while the narrower cavity-appearance experiment may return later as a new, linked candidate. The human is being asked whether a previous case-specific exception should override the repository's written rule requiring that outcome.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Add an independently validated brain-reserve measurement or intervention with a prespecified contrast that separates reserve use from age, vascular-disease burden, and bare cavity-morphology association; otherwise route the narrower NCCT-channel study as a new lineage-linked candidate."}
```
