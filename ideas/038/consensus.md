# Debate summary — idea 038

## Agreed

- In round 1, both sides agreed that the destination swap changes arterial-border distance only by changing anatomical position and receptive-field context. The resulting response cannot distinguish use of border distance from sensitivity to coordinate, surrounding anatomy, multiscale perfusion context, or patch compatibility.
- In round 1, both sides agreed that neither averaging over many matched pairs nor the parallel-boundary sham repairs the problem. Averaging does not remove systematic destination differences, and the sham controls displacement and interpolation but not the different destination context.
- In rounds 1 and 2, both sides agreed that the failure is constitutive for the proposed image-only measurement design and precedes the common-support and realism gates. More cases, a successful support census, a discriminator, or checkpoint acquisition would not identify the claimed mechanism.
- In rounds 1 and 2, both sides agreed that the checkpoint-free association study is scientifically defensible but asks a different question. It must be registered as a new candidate with `parent_ids`, undergo its own novelty audit, and inherit no queue position.
- In round 2, both sides agreed that no public frozen ISLES'24 final-infarct checkpoint was located, but that this is a separate unresolved access fact rather than the reason to reject idea 038.
- In round 2, both sides agreed on the revisit condition: a new design would have to manipulate a validated arterial-border variable independently of coordinate and receptive-field context, or provide a negative control that uniquely excludes coordinate/context sensitivity.

## Unresolved

No substantive disagreement remains.

The availability of an obtainable frozen final-infarct checkpoint remains factually unresolved, but the parties do not disagree about its status or its role. The proposer and critic both treat it as an open access question, separate from the rejection rationale. A released checkpoint, an obtainable participant container, or documented reproducible training of a suitable frozen model would settle access, but would not repair the identified confounding.

The stated revisit condition may be impossible for this image-only measurement class because arterial-border distance is encoded through position and context. Neither side identified an available experiment satisfying it. Evidence that could reopen the question would be a concrete measurement design demonstrating independent manipulation of a validated border variable while preserving coordinate and effective receptive-field context, or a uniquely discriminating negative control; absent such a design, the original estimand remains unidentifiable.

## Positions that moved

- The proposer conceded in round 1 in response to the critic's specific argument that relocation jointly changes border distance, absolute coordinate, anatomy, and receptive-field context. This was an earned concession: the proposer separately tested the two defenses available on the card—many-pair averaging and the parallel-boundary sham—and explained why neither separates the mechanism.
- The critic moved from `OPEN` in round 1 to `CONVERGED` in round 2 after the proposer supplied the stronger constitutive argument that an image-only model has no independently manipulable border-distance channel and accepted the claim-identity consequence.
- The proposer conceded again in round 2 to formalize the agreed disposition, revisit trigger, and separation of checkpoint access from the kill rationale. This introduced no new substantive concession and was not unearned capitulation; it recorded the already-supported round-1 agreement.

## Amendments made

Idea 038 itself was not amended into a surviving design. At round zero it claimed that a destination-swap response could show that a final-infarct model uses proximity to an arterial border zone as a tissue-vulnerability prior beyond local perfusion severity. After debate, both sides concluded that the proposed response supports only sensitivity to a border-zone-typed destination under synthetic transplantation, because the border coordinate cannot be separated from location and context.

The proposed replacement is a separate successor: test whether uncertainty-aware arterial-territory border distance adds held-out prediction of follow-up infarction beyond acute perfusion maps and prespecified anatomical and occlusion covariates in the 149 public ISLES'24 cases. What is lost is the model-use claim, the causal interpretation of a learned vascular “last-mile” prior, and any physiological claim about pressure reserve or collateral redundancy. The successor would be association-only and checkpoint-free.

## Recommendation

**REJECT.** The destination-swap design cannot separate the claimed arterial-border mechanism from anatomical coordinate and receptive-field context in an obtainable image-only experiment. The single most important thing for the human to inspect is whether any genuinely new measurement design can meet the agreed revisit condition; the association-only proposal should not be treated as a repair because it changes the deliverable question.

## In plain terms

This idea asks whether a stroke model assigns extra risk to tissue near the boundary between arterial territories even when measured blood-flow damage looks similar. It proposed testing that by moving the same image patch between interior and border-zone locations.

The debate concluded that moving the patch inevitably changes its anatomical location and surrounding image context at the same time as border distance. A model response therefore could not show that border distance itself caused the change, and the proposed controls cannot separate those explanations. A simpler study of whether border distance predicts later infarction may still be worthwhile, but it is a new association question rather than evidence about what an existing model uses.

The human is being asked to reject this design unless a new experiment can vary arterial-border information independently of location and surrounding image context.

```json
{"verdict":"KILL","kill_code":"IDENTIFIABILITY_FAILURE","unblock":"Provide a new measurement design that independently manipulates a validated arterial-border variable while holding coordinate and effective receptive-field context fixed, or a negative control that uniquely excludes coordinate/context sensitivity."}
```
