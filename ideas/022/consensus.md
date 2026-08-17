# Debate summary — idea 022

## Agreed

- The original study requires an obtainable, frozen raw-4D-CTP final-infarct model with non-trivial held-out performance and inspectable training-time temporal masking or padding semantics. Both sides accepted this requirement in round 1.
- The published ISLES'24 winner is not the required study object because it consumes CTA and derived perfusion maps rather than raw 4D CTP. Both sides accepted this in round 1.
- The closest public raw-CTP implementation, ISLES24-PrediCTP, supplies code but no frozen checkpoint, documents no training-supported prefix representation, and reports performance too weak to anchor the proposed entry-point-2 model audit. The proposer independently checked and accepted these facts in round 1.
- Retraining PrediCTP or training a replacement would not preserve the question: the experimenter's padding, masking, or temporal augmentation choices would partly install the behavior being audited. Both sides agreed in round 1 that this would require a successor candidate under the claim-identity rule.
- A checkpoint without documented training support for the prefix representation would retain the intervention-validity problem seen in idea 006; agreement on this point was explicit in rounds 1 and 2.
- The nested-prefix design itself remains coherent and should be retained for use if the missing study object becomes available. Both sides accepted this by round 1 and reaffirmed it in round 2.
- The proposed model-free censoring–severity audit has a different estimand and therefore must be registered separately with `parent_ids: [idea-022]`, rather than treated as a repair to idea 022. Both sides agreed in rounds 1 and 2.
- The proper present disposition is PAUSE for lack of an obtainable study object, with the failure pattern corresponding to DATA_ACCESS. Agreement was reached in round 1 and reaffirmed in round 2.

## Unresolved

There is no live disagreement between proposer and critic after round 1. The remaining questions are factual unblock conditions rather than disputed positions:

- **Does an obtainable, performant frozen raw-4D-CTP final-infarct checkpoint exist or become available?** The proposer and critic both say none was found in the inspected repositories, artifact services, or challenge releases. A released checkpoint, or checkpoint access obtained through author correspondence, together with documented held-out performance would settle this clause.
- **Were shorter-prefix masks or padding representations supported during that model's training?** Both sides require direct inspection rather than inference. The actual training loader, frozen configuration, or sufficiently explicit primary methods documenting the temporal mask/padding and augmentation semantics would settle it.
- **Are enough ISLES'24 acquisitions temporally complete to support the planned nested prefixes?** Neither side claims this has been inspected. A header and curve-completeness census of the released cases—potentially produced by the separate dataset-side audit—would settle it.

## Positions that moved

- In round 1, the proposer conceded the critic's fatal objection that the required study object is not obtainable. The concession responded to concrete evidence: the winner's derived-map inputs, the absence of a PrediCTP checkpoint and documented prefix semantics, its weak reported performance, and the claim-identity problem created by retraining. The proposer independently inspected the repository and searched for alternative artifacts before conceding. This was an earned concession, not capitulation.
- In round 2, the proposer reiterated the round-1 concession after the critic stated that the evidence resolved the dispute and introduced no new objection. This was confirmation of an already supported agreement, not an additional concession; it is not UNEARNED.

The debate converged after one substantive objection-and-response round, but this was not a no-objection or rubber-stamp convergence: the critic raised a fatal, evidence-backed objection that changed the disposition from a runnable candidate to a paused one.

## Amendments made

No amendment to the original idea was adopted. The original claim remains a model-use claim: a frozen raw-CTP final-infarct model uses terminal-curve incompleteness as a tissue-fate cue. That claim is paused because its required model artifact is unavailable.

The parties explicitly declined three changes that would have altered the claim: auditing the derived-map winner, retraining PrediCTP, or training a new raw-CTP model. The model-free censoring–severity audit was retained only as a proposed successor. What is lost for now is executable model-use inference and any prospect of reaching rung 1; the nested-prefix identification design is preserved for a future unpause.

## Recommendation

**PAUSE.** The single most important thing for the human to inspect is whether a frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance can actually be obtained together with its training-time temporal masking or padding semantics. Both parts are necessary; a checkpoint alone would not validate the prefix intervention.

```json
{"verdict": "PAUSE", "unblock": "Obtain a frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance and directly inspect training-time temporal masking or padding semantics that support the nested-prefix intervention."}
```
