# Debate summary — idea 006

## Agreed

- The original patient-deletion intervention is an extreme distribution shift and cannot identify whether CT-CLIP uses exterior information during intact-image inference (proposer conceded in round 1; critic recorded convergence in round 2).
- Inspecting `data_inference_nii.py` established that exterior voxels survive inference preprocessing, but did not establish the load-bearing keystone that a body-excluded volume is in-distribution for the released checkpoint. Both sides agree this repeated the C3 structure seen in idea 005: the easy fact was verified while the fact required by the inference was assumed (round 1).
- The proposed scrambled-exterior control does not repair the design because both arms retain the dominant patient-deletion shift. A deletion-shift-matched featureless-air control would still compare off-manifold inputs and therefore would not establish reliance during intact inference (round 1).
- Neither direction of the original result supports the motivating claim. A positive could reflect extrapolation, artificial boundaries, positional or preprocessing effects; a negative could occur because deletion destroys the anatomical context through which an exterior cue operates (round 1).
- Consequently, the anticipated negative is uninterpretable for the motivating causal claim, not decisive, and `negative_result_value` must be capped at 2. The keystone must revert from `INSPECTED_TRUE` to `NOT_INSPECTED`, while feasibility and novelty confidence must be capped at 3 (round 1).
- The original language about the fraction of AUROC that “survives” overstates what a highly non-additive occlusion experiment can decompose (round 1).
- Retraining on ablated inputs, as motivated by Hooker et al. (arXiv:1806.10758), or learning a valid conditional anatomy generator, as motivated by Chang et al. (arXiv:1807.08024), would address parts of the distribution-shift problem but falls outside this study's stated single-GPU scope (rounds 1–2).
- The exterior-swap proposal is scientifically defensible but changes the estimand: it asks whether intact-image predictions are sensitive to exterior identity, not how much abnormality performance remains after deleting the patient. It should be assessed from scratch rather than treated as a repair of this card (rounds 1–2).
- The current candidate should remain paused unless checkpoint-specific evidence makes the deletion intervention supported by the model's training distribution (round 2).

## Unresolved

### Did CT-CLIP training make large constant-filled occlusions sufficiently familiar?

- **Question:** Did the official CT-CLIP training pipeline use large-region masking, cutout, or comparable augmentation with the same fill convention, such that body exclusion is materially less off-manifold for this checkpoint?
- **Proposer's position:** This is an uninspected, concrete reopening possibility. If such augmentation was used, the keystone becomes an empirical question of degree rather than automatically false; if it was not used, the pause is effectively permanent for CT-CLIP.
- **Critic's position:** The critic requires a validated intervention supported by a primary-source training rationale or direct distributional validation. The critic did not separately evaluate the newly raised possibility because it appeared after convergence.
- **What evidence would settle it:** Direct inspection of the official training loader, augmentation configuration, and training methods, followed—if relevant augmentation exists—by direct validation that the proposed body-excluded inputs fall within the checkpoint's supported input distribution. Code inspection alone could rule the possibility out but would not by itself prove the intervention valid.

### Could the original question be valid for a different chest-CT model?

- **Question:** Would a model pretrained with sufficiently similar large blanked regions make the original patient-removal estimand interpretable?
- **Proposer's position:** Possibly; a masked-reconstruction or suitably augmented encoder may already incorporate the remedy during pretraining. This would be a new candidate because the present card names CT-CLIP ClassFine.
- **Critic's position:** The critic's stated reopening criterion allows a different validated intervention/model in principle, but no such model or validation was presented in the debate.
- **What evidence would settle it:** A directly inspected training objective and corruption process that closely matches complete body removal, plus empirical distributional and task validation showing that this intervention is supported. Generic masked pretraining alone would not settle equivalence to removing nearly all anatomy.

## Positions that moved

- **Proposer, round 1:** Conceded the fatal objection in response to the critic's argument that constant-filled patient deletion creates distribution-shift ambiguity in both positive and negative results, and that the scrambled-exterior control shares rather than removes that ambiguity. This was an earned concession: the proposer added directly inspected methodological support from Hooker et al. and Chang et al., traced the consequences through the keystone and scores, and performed an explicit identity check on the proposed repair.
- **Critic, round 2:** Moved from an open fatal objection to convergence after the proposer accepted the objection, supplied supporting methodological evidence, and declined to disguise the exterior-swap study as an amendment. This was not a concession on substance; it recorded resolution of the objection.
- **Proposer, round 2:** Conceded that no remaining defence had been offered and accepted PAUSE. No new adverse argument was introduced in that round, but this is not an UNEARNED capitulation: it confirms the already supported round-1 concession while adding checkable revisit conditions.

## Amendments made

The transcript identifies required changes to the card, although `idea_card.json` had not yet been updated during the debate:

- Recommendation changes from `SHORTLIST` to `PAUSE`.
- `keystone_status` changes from `INSPECTED_TRUE` to `NOT_INSPECTED`; the evidence now supports only exterior retention by inference preprocessing, not in-distribution body deletion.
- Feasibility and novelty confidence are capped at 3 pending an inspected true keystone.
- The anticipated negative changes from decisive to uninterpretable for the motivating claim, and negative-result value is capped at 2.
- `dies_like_prior` no longer claims immunity from prior failure modes; it acknowledges the same wrong-keystone structure as idea 005, although the substantive issue here is intervention validity rather than annotation provenance.
- The 4.10 priority score must be recomputed from the revised scores.
- Claims that the primary readout establishes exterior use, that the secondary AUROC is a lower bound on artifact, and that the controls isolate signal from prior or mask leakage are withdrawn for the original intervention.

What is lost is the card's central estimand and headline: the debate found no in-scope way to interpret “diagnose a volume with no patient in it” as evidence about normal CT-CLIP inference. The exterior-swap study retains the medical motivation but is explicitly a separate question, not an amendment. The only retained path for this card is a checkpoint-specific reopening based on previously uninspected training augmentation or a future reformulation around another appropriately trained model.

## Recommendation

**PAUSE.** Before deciding whether the pause is reversible, the human should inspect the official CT-CLIP training data loader and augmentation configuration for large-region masking or cutout with a matching fill value. Absence would make the original intervention indefensible for this checkpoint; presence would justify distributional validation, not automatic advancement.
