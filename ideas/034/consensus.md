# Debate summary — idea 034

## Agreed

- By round 1, both sides agreed that the original cross-patient observational stage 2 cannot distinguish use of the CTP slab boundary from ordinary use of perfusion evidence that is present inside the slab and absent outside it. Matching on anatomy, NCCT, CTA, or lesion volume does not repair that confounding.
- By round 1, both sides agreed that the model-free census is identifiable and worthwhile: measure lesion volume and lesion components outside CTP support in the 149 released training cases, report a clearly named CTP-support-confined oracle Dice, and avoid claims about leaderboard movement without actual submissions and official rank aggregation.
- By round 1, both sides agreed that retaining only this census changes the deliverable from a model-use claim to a benchmark-integrity audit. Under the claim-identity rule it must therefore be registered as a successor, not treated as a repair of idea 034.
- By round 1, both sides agreed that any model experiment must use an obtainable frozen checkpoint on held-out data, preserve tested-voxel inputs bit-for-bit, freeze any per-instance normalization from the unedited case, and price model acquisition or training honestly. The card's shared audit model and sub-five-GPU-hour stage-2 estimate were not verified.
- By round 2, both sides agreed that, for a mask-free model, the observable support edge is constituted by the transition from valid perfusion-map content to the release's empty-region fill. Fill runs, discontinuities, and boundary detection cannot simply be treated as independently manipulable internal cues.
- By round 2, both sides agreed that marginally realistic slab width is insufficient to establish that truncating a particular wide-slab case creates an in-distribution joint input. Scanner, protocol, placement, anatomy, and perfusion content may covary.
- By round 2, both sides agreed that pipeline inspection is a necessary first gate: an explicit support/valid-mask channel or a support-derived crop would materially change what intervention is possible.
- By round 3, both sides agreed that the mask-free terminal-truncation intervention is composite: it both relocates the content-to-fill transition and deletes all distal perfusion activations. The proposed interior fill band controls some fill/discontinuity effects but does not hold terminal deletion constant.
- By round 3, both sides agreed that matching synthetic-edge behavior to the same checkpoint's behavior at real edges may serve as a falsification gate for artifacts, but cannot verify the disputed boundary-use attribution because real-edge behavior is itself confounded.
- By round 3, both sides agreed that a battery of known-mechanism reference models establishes discrimination only over the mechanisms included in that battery; it cannot exclude unenumerated alternatives such as one-sided context aggregation or volume-wide pooling.
- By round 3, both sides agreed that the currently buildable mask-free experiment supports at most a narrower claim about sensitivity to terminal CTP truncation, not the original claim that the model uses boundary position as a spatial stopping rule rather than the ischemia's edge. That narrower claim is a successor.

## Unresolved

### Could an explicit-mask checkpoint revive the original question?

- **Question:** Does an obtainable frozen ISLES'24 checkpoint consume an explicit support/valid-mask channel that was varied during training independently enough of perfusion content to permit an in-support mask-position intervention with all map voxels fixed?
- **Proposer's position:** This is an inspectable branch that could retain the original claim if the channel exists and its intervention lies within the checkpoint's trained joint support.
- **Critic's position:** This is the only presently described route that could preserve the original claim, but the required checkpoint property and training variation are uninspected; an explicit channel alone is insufficient without evidence that mask-only changes are supported by training.
- **What evidence would settle it:** Direct inspection of an obtainable checkpoint's architecture, preprocessing, and training pipeline; evidence of sufficiently independent support-mask variation during training; and a held-out intervention showing that mask-position changes alter predicted extent while matched distal-content interventions do not. If no such checkpoint exists, this revival route closes.

### Can a mask-free acquisition or intervention ever separate edge position from distal context?

- **Question:** Is there an obtainable, validated mask-free intervention or acquisition pair that varies terminal support position independently of distal perfusion context?
- **Proposer's final position:** No currently specified intervention does so; the truncation study must be recast as a successor with a truncation-sensitivity claim.
- **Critic's position:** Without such an independent contrast, edge-position use is not identifiable in mask-free inputs.
- **What evidence would settle it:** A validated acquisition pair or generative intervention that independently crosses terminal support position and distal perfusion content while preserving local inputs and joint-support realism. No such evidence was presented. There is no remaining disagreement about the currently proposed design; this is a future empirical revival condition.

## Positions that moved

- **Proposer, round 1:** Conceded the critic's original objection that the cross-patient in-slab/out-of-slab comparison cannot support the deliverable sentence. This moved in response to the argument that slab membership necessarily changes local perfusion-evidence availability. The proposer also accepted that the model-free census is a separate successor if stage 2 is removed, that the oracle and leaderboard language were overstated, and that model cost and availability were understated.
- **Critic, round 2:** Accepted the narrower logical point that, in mask-free released inputs, the support boundary and content-to-fill transition are constitutively linked, so fill-run, discontinuity, and boundary-detection mechanisms need not be treated as independently observable cues. This moved in response to the proposer's explanation that the supposed factorial cell with a boundary but preserved valid content beyond it is contradictory in that input representation. The critic did not accept that this resolves terminal-deletion confounding.
- **Proposer, round 2:** Conceded that pipeline mask semantics were uninspected, marginal geometry was not adequate realism evidence, and generic fill/discontinuity sensitivity required controls. This moved in response to the critic's explanation that the first amended donor-content arm did not reproduce deletion into empty fill and could not isolate the claimed mechanism.
- **Proposer, round 3:** Conceded the entire remaining mask-free use claim. This moved in response to the new argument that terminal truncation changes not only the transition location but also the total distal activation mass, leaving one-sided aggregation and global pooling as compatible explanations. The proposer also conceded the circular use of real-edge behavior as verification and the insufficiency of a finite reference-model battery. This concession was earned, not capitulation.
- No concession was UNEARNED. The debate did not converge in one round; the critic raised distinct, progressively more specific objections across three rounds.

## Amendments made

At round zero, the card claimed that a cross-patient boundary-discontinuity analysis could show that a final-infarct model used the perfusion-acquisition support boundary as a spatial determinant of predicted lesion extent, while stage 1 would quantify target overflow and its benchmark consequences.

Round 1 replaced the observational model analysis with a paired within-case truncation intervention at retained voxels, added a distal-content substitution arm, narrowed the scope to one frozen held-out checkpoint, and corrected stage 1 to report a CTP-support-confined oracle Dice rather than a general performance ceiling or unsupported leaderboard effect. It also acknowledged GPU-day-scale model costs and made a workable in-distribution edit a kill gate.

Round 2 added pipeline inspection, an explicit-mask branch, a real-edge behavioral falsification gate, an interior empty-fill band, and validation on known-mechanism reference models. In the mask-free branch, the proposed claim was operationally narrowed to response to the terminal content-to-fill transition, without asserting an internal boundary-detection mechanism. Cost and kill gates increased further.

Round 3 withdrew the mask-free confirmatory claim altogether. The surviving products are not amendments to idea 034 but separate candidates:

- a model-free released-training-cohort audit of lesion volume and components outside CTP support, with a precisely constrained oracle Dice and no leaderboard claim;
- a checkpoint-specific terminal-truncation-sensitivity study with no edge-versus-ischemia attribution;
- a possible revival of the original question only if an inspected checkpoint provides an independently trained and manipulable support-mask channel, or an equivalent independent contrast becomes obtainable.

What was lost is the central deliverable sentence of idea 034: no currently specified, physically realizable mask-free design separates use of boundary position as a stopping rule from co-varying deletion of distal perfusion evidence.

## Recommendation

**REJECT.** Record idea 034 as killed for `IDENTIFIABILITY_FAILURE`, while allowing the model-free overflow census and the narrower truncation-sensitivity experiment to enter separately through the normal successor pipeline.

The single most important thing for the human to inspect before deciding is whether an obtainable frozen checkpoint actually consumes an explicit support/valid-mask channel that was varied independently of perfusion content during training. That fact is the only concrete route identified in the debate that could revive the original edge-rather-than-ischemia question; it does not rescue the current card without inspection and validation.

## In plain terms

This idea asks whether a stroke model stops or extends its predicted damage according to where the perfusion scan ends, rather than where the injured tissue ends. It also proposes counting how much of the benchmark's later-MRI lesion lies outside the area covered by the earlier perfusion scan.

The debate concluded that the counting audit is useful, but it is a separate question. For ordinary model inputs, moving the scan edge also deletes all perfusion information beyond that edge, so the proposed experiments cannot tell whether the model uses the edge itself or merely reacts to the missing information. The original idea should therefore be rejected, while the coverage audit and a more modest truncation-sensitivity study may be proposed as successors.

The human is being asked to check whether a real frozen model has a separately manipulable support-mask input that was varied during training; only that could reopen the original question on the evidence identified here.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Inspect an obtainable frozen checkpoint and verify an explicit support/valid-mask channel varied independently during training enough to support an in-distribution mask-position intervention with all perfusion-map voxels fixed, or obtain an equivalent independent acquisition contrast."}
```
