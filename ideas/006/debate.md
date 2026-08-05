# Debate transcript

## Round 1 — CRITIC

**Position:** Replacing the entire patient with a constant creates an extreme out-of-distribution input, so its scores cannot identify whether CT-CLIP uses exterior signal on intact CT volumes.

**Argument:** The inspected official `data_inference_nii.py` establishes only that preprocessing retains exterior voxels; it does not establish that a nearly anatomy-free volume resembles the model's training distribution. On the proposed B input, abnormality-score variation or above-chance AUROC could arise from extrapolation, the artificial body-mask boundary, positional embeddings, padding/cropping geometry, or interactions between those artifacts and the retained exterior. Conversely, chance AUROC could occur because deleting anatomy destroys the feature context required to use an exterior cue. The scrambled-exterior control does not resolve this because both B and D share the dominant patient-deletion shift. Thus neither a positive nor a negative answers the claimed rung-1 question of exterior use during normal inference, and the stated `INSPECTED_TRUE` keystone verifies the wrong fact.

**What would change my mind:** Direct evidence that the body-excluded intervention is within the model's supported input distribution and that, on intact scans with identical body voxels, controlled exterior substitutions produce effects exceeding matched sham-compositing and seam controls; absent that, the defensible exterior-swap study is a changed question and should not validate the original “diagnose a volume with no patient” design.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** Blanking the entire body produces an input unlike anything the model was trained on, so a score computed on it is a measurement of the network's extrapolation behaviour and not of whether the network uses exterior content when it reads a real chest CT. Above-chance AUROC on that input could come from the synthetic body/exterior boundary, positional encodings or crop-and-pad geometry rather than from exterior signal; chance AUROC could come from the model collapsing under the distribution shift before any exterior cue it does use on intact scans has a chance to express itself. The scrambled-exterior control cannot separate these because both arms carry the same patient-deletion shift. Therefore the keystone I marked `INSPECTED_TRUE` verified the wrong fact: the script proves the exterior survives preprocessing, not that a body-excluded volume is an input the model supports.

**Response:** CONCEDE

**Argument:** The objection is correct, and the primary-source position is worse for me than the critic put it.

Hooker, Erhan, Kindermans and Kim state my error almost word for word (*A Benchmark for Interpretability Methods in Deep Neural Networks*, arXiv:1806.10758; verified by reading the ar5iv HTML of the paper body, not the abstract): "Samples where a subset of the features are removed come from a different distribution... Therefore, this approach clearly violates one of the key assumptions in machine learning: the training and evaluation data come from the same distribution," and "The replacement value c can only be considered uninformative if the model is trained to learn it as such. Without retraining, it is unclear whether degradation in performance is due to the introduction of artifacts outside of the original training distribution or because we actually removed information." Chang, Creager, Goldenberg and Duvenaud make the same point about the fill value specifically (*Explaining Image Classifiers by Counterfactual Generation*, arXiv:1807.08024, ICLR 2019; abstract read directly): constant, blur and noise in-fills "generate inputs far from the data distribution."

The reason this closes the matter rather than opening a repair is the remedy those authors adopt. ROAR's answer is to retrain the model on the ablated inputs so that the replacement value is learned as uninformative. CT-CLIP is a contrastively pretrained 3D encoder trained on tens of thousands of volumes; retraining it is outside the charter's single-GPU compute envelope, so the sanctioned remedy is unavailable to me. FIDO's answer is generative in-filling, which would require a conditional generative model of chest-CT anatomy — a larger project than the study it would be a control for. I have no third remedy that leaves the question intact.

What this costs the card, concretely, and I am recording all of it rather than the minimum:

- `keystone_status` must revert from `INSPECTED_TRUE`. The keystone has two clauses joined by AND. I verified the first (the preprocessing pipeline retains exterior voxels at full dynamic range) and asserted the second (a body-excluded input is therefore in-distribution) as though it followed. It does not follow, and ROAR says it is false by construction. This is the C3 error the charter names, committed again: I verified the fact that was easy to check rather than the fact my inference needed.
- Under the hard cap, `feasibility` returns to 3 and `novelty_confidence` to 3 at most.
- `anticipated_negative.classification` was "decisive" and cannot be. The critic's mechanism — exterior cues that only operate jointly with anatomical features would be silenced by the very intervention meant to expose them — makes a chance result type 3, uninterpretable, for the motivating claim. `negative_result_value` of 4 was unsupportable.
- The estimand itself was misdescribed. "How much of the AUROC survives" reads as a decomposition of intact performance into anatomical and non-anatomical parts. Non-additivity of occlusion when nearly the whole input is replaced means no such decomposition is licensed by this measurement, whatever number comes out.
- I withdraw the claim in `dies_like_prior` that "no prior failure mode applies." The failure mode is not annotation provenance, so it is new to this ledger, but the deeper pattern — a keystone whose easy clause was inspected and whose load-bearing clause was assumed — is exactly how idea 005 died. I asserted immunity to the ledger's lesson while repeating its structure.

One thing I want on the record without offering it as a rebuttal, because it is not one. The critic's round-1 argument defeats the D control as I specified it, but a deletion-shift-matched contrast does exist: B against a copy of B whose exterior is replaced with synthetic featureless air at matched mean and variance, holding the patient-deletion shift exactly fixed and varying only whether real exterior texture is present. That contrast is better than D. It still compares two off-manifold points, so by ROAR's argument a difference between them says the encoder's response to synthetic inputs depends on exterior content, and says nothing about intact inference. It does not rescue the question and I am not amending toward it.

**Identity check on the repair I am declining to submit:** the critic's exterior-swap design — every voxel inside a dilated body contour held fixed, matched exterior substituted — asks whether intact-image predictions are sensitive to exterior identity. The original question asks how much abnormality AUROC survives deleting the patient. These are different estimands with different failure modes; the swap design would be a defensible study and would not answer the question on the card. Per the rules an amendment that reaches feasibility by replacing the motivating question is not a repair, so I am not submitting it. It is recorded below as a spin-off, and it belongs to the critic, who proposed it.

**Spin-off:** Holding every voxel inside a dilated patient contour fixed, do matched substitutions of the scan exterior change CT-CLIP ClassFine abnormality scores and patient-clustered validation performance beyond sham-recomposition and seam controls? Its own keystone — that matched swaps can be composited close enough to the observed exterior distribution for the comparison to be controlled — is uninspected, and it inherits the gated-checkpoint access question that this card also never verified. It should be scored from scratch as a new candidate, not inherited from this one.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has established that the original patient-deletion design is invalid and cannot be repaired without changing its estimand.

**Argument:** CONCEDED. The proposer supplied the missing methodological argument and performed the identity check correctly: Hooker et al. (arXiv:1806.10758) show that constant feature removal creates distribution-shift ambiguity unless the model is retrained on the ablated distribution, while Chang et al. (arXiv:1807.08024) identify constant in-fills as off-manifold counterfactuals. More importantly, the proposer explicitly accepts that neither the deletion-shift-matched contrast nor an exterior-swap amendment answers the card's original question of how much abnormality AUROC survives removal of the patient. The former remains an off-manifold stress test; the latter asks a different, defensible question about sensitivity during intact-image inference. Because retraining CT-CLIP or learning a valid conditional anatomy generator is outside the stated compute envelope, no in-scope repair preserves the original estimand. The current candidate should therefore remain paused, and the exterior-swap study should be evaluated separately from scratch.

**What would change my mind:** A validated intervention that removes patient anatomy while keeping inputs within CT-CLIP's supported distribution—demonstrated by a primary-source training rationale or direct distributional validation—and that preserves the original AUROC-survival estimand without retraining beyond the compute constraint.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic accepts the concession, agrees the identity check was performed correctly, and holds that no repair inside the compute envelope preserves the original AUROC-survival estimand, so the candidate stays paused and the exterior-swap study is scored from scratch.

**Response:** CONCEDE

**Argument:** No remaining defence. I am using this round only to make the revisit trigger checkable rather than rhetorical, because the critic's "what would change my mind" as stated is a condition nobody could evaluate without new work, and a PAUSE with an unevaluable reopening condition is a REJECT wearing a softer word.

Two concrete facts would satisfy it, and neither has been inspected:

1. **The training-side augmentation pipeline of CT-CLIP.** I read `scripts/data_inference_nii.py`, which is the *inference* preprocessing path. I did not read the training data loader or its augmentations. ROAR's condition is that the replacement value be learned as uninformative — and that can be satisfied by training-time augmentation, not only by retraining after the fact. If the official training pipeline applies random large-region masking, cutout, or masked-autoencoder-style occlusion with a fixed fill value, then a body-excluded volume with that same fill value is substantially less off-manifold than I have been assuming, and the keystone's second clause becomes a question of degree rather than a construction error. If it applies no such augmentation, the second clause is dead for this checkpoint and the pause is permanent for CT-CLIP specifically. This is hours of reading in a public repository and it is the single cheapest thing that could move this card. I should have read it before writing `INSPECTED_TRUE`, and the fact that I inspected the inference script instead is the same shortcut the charter warns about — I read the file that was easy to find rather than the file my inference needed.

2. **A different model.** The objection is checkpoint-specific, not question-specific. A chest-CT encoder pretrained with a masked-reconstruction objective has large blanked regions in its training distribution by construction. The original question — how much abnormality performance survives when the patient is removed — would be askable of such a model without ROAR's remedy, because the remedy is already in its pretraining. That is not an amendment to this card, since this card names the released CT-CLIP ClassFine checkpoint; it is a note that the question survives the model even though it does not survive this model.

For the record, the card changes that follow from round 1 and are not yet written to `idea_card.json`: `keystone_status` reverts to `NOT_INSPECTED`; `feasibility` and `novelty_confidence` capped at 3; `anticipated_negative.classification` becomes uninterpretable and `negative_result_value` capped at 2 accordingly; `dies_like_prior` rewritten to name the shared structure with idea 005 rather than claiming immunity; `recommendation` becomes PAUSE. The priority score should be recomputed from those values rather than carried forward at 4.10.

**Status:** CONVERGED
